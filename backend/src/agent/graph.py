"""Modified LangGraph implementation supporting multiple LLM providers."""

import os
from typing import Any, Dict, List

# Use absolute imports for LangGraph compatibility
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig

from state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from configuration import Configuration
from prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from llm_factory import LLMFactory
from web_search_tool import web_search_tool
from utils import (
    get_research_topic,
)
# Import RAG functions locally to avoid circular imports
# from rag_nodes import rag_retrieve, should_use_rag, rag_fallback_to_web

load_dotenv()

# Check if any API key is available
def check_api_keys():
    """Check if at least one LLM API key is configured."""
    if not any([
        os.getenv("DEEPSEEK_API_KEY"),
        os.getenv("ZHIPUAI_API_KEY"), 
        os.getenv("QWEN_API_KEY"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("LLM_API_KEY")
    ]):
        raise ValueError("At least one LLM API key must be configured. Please set one of: DEEPSEEK_API_KEY, ZHIPUAI_API_KEY, QWEN_API_KEY, OPENAI_API_KEY, or LLM_API_KEY")

check_api_keys()


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """LangGraph node that generates search queries based on the User's question."""
    configurable = Configuration.from_runnable_config(config)

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # init LLM
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
    )

    # Format the prompt to request plain text output
    current_date = get_current_date()
    
    # Safely get research topic from messages
    messages = state.get("messages", [])
    if not messages:
        # Use a default research topic if no messages are available
        research_topic = "General research topic"
    else:
        research_topic = get_research_topic(messages)
    
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=research_topic,
        number_queries=state["initial_search_query_count"],
    ) + "\n\nPlease provide search queries as a simple list, one per line."
    
    # Generate the search queries
    result = llm.invoke(formatted_prompt)
    
    # Extract content and parse queries
    if hasattr(result, 'content'):
        content = result.content
    else:
        content = str(result)
    
    # Debug output
    print(f"DEBUG: generate_query LLM response: {content}")
    
    # Parse the JSON response to extract queries
    queries = []
    try:
        import json
        import re
        
        # Try to extract JSON from the response
        # Look for JSON block between ```json and ```
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            # Try to parse the entire content as JSON
            json_content = content
        
        # Parse JSON
        parsed_json = json.loads(json_content)
        
        # Extract queries from the parsed JSON
        if isinstance(parsed_json, dict) and 'query' in parsed_json:
            query_list = parsed_json['query']
            if isinstance(query_list, list):
                queries = [str(q).strip() for q in query_list if q]
            elif isinstance(query_list, str):
                queries = [query_list.strip()]
        
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        print(f"DEBUG: JSON parsing failed: {e}")
        # Fallback to original text parsing
        for line in content.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//') and not line.startswith('{') and not line.startswith('}'):
                # Remove numbering and bullet points
                line = line.lstrip('0123456789.-• ')
                if line and '"' not in line:  # Skip lines with quotes (likely JSON)
                    queries.append(line)
    
    # Ensure we have at least one query
    if not queries:
        queries = [research_topic]
    
    print(f"DEBUG: Parsed queries: {queries}")
    
    return {"search_query": queries[:state["initial_search_query_count"]]}





def web_research(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """LangGraph node that performs web research using configured search engines."""
    configurable = Configuration.from_runnable_config(config)
    
    # Get the current search query (handle both string and list formats)
    current_query = state["search_query"]
    if isinstance(current_query, list) and current_query:
        # If it's a list, take the last query
        query_text = current_query[-1] if isinstance(current_query[-1], str) else str(current_query[-1])
    else:
        query_text = str(current_query)
    
    # Debug output
    print(f"DEBUG: web_research called with query: {query_text}")
    print(f"DEBUG: web_research state search_query: {state['search_query']}")
    print(f"DEBUG: web_research state search_query type: {type(state['search_query'])}")
    
    # Perform web search
    search_results = web_search_tool.search(query_text, max_results=5)
    
    # Debug output
    print(f"DEBUG: search_results from web_search_tool: {search_results}")
    print(f"DEBUG: search_results type: {type(search_results)}")
    print(f"DEBUG: search_results length: {len(search_results) if search_results else 0}")
    
    # Format search results for the LLM
    formatted_results = web_search_tool.format_search_results(search_results)
    
    # Create LLM to analyze and summarize the search results
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0,
        max_retries=2,
    )
    
    # Create a prompt to analyze the search results
    analysis_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    ) + f"\n\nSearch Results:\n{formatted_results}\n\nPlease provide a comprehensive analysis of these search results."
    
    # Get LLM analysis
    analysis_result = llm.invoke(analysis_prompt)
    
    # Extract content from the response
    if hasattr(analysis_result, 'content'):
        analysis_text = analysis_result.content
    else:
        analysis_text = str(analysis_result)
    
    # Create sources list
    sources_gathered = [
        {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "snippet": result.get("snippet", "")
        }
        for result in search_results
    ]
    
    # Debug output
    print(f"DEBUG: sources_gathered created: {sources_gathered}")
    print(f"DEBUG: sources_gathered length: {len(sources_gathered)}")
    
    result_dict = {
        "sources_gathered": sources_gathered,
        "search_query": state["search_query"],  # Keep the original format
        "web_research_result": [analysis_text],
    }
    
    print(f"DEBUG: returning result_dict: {result_dict}")
    
    return result_dict


def reflection(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries."""
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    current_loop_count = state.get("research_loop_count", 0)
    state["research_loop_count"] = (current_loop_count or 0) + 1
    reasoning_model = state.get("reasoning_model", configurable.reflection_model)

    # Format the prompt
    current_date = get_current_date()
    web_research_result = state.get("web_research_result", [])
    summaries_text = "\n\n---\n\n".join(web_research_result) if web_research_result else "No research content available."
    
    # Safely get research topic from messages
    messages = state.get("messages", [])
    if not messages:
        research_topic = "General research topic"
    else:
        research_topic = get_research_topic(messages)
    
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=research_topic,
        summaries=summaries_text,
    )
    
    # init Reasoning Model
    llm = LLMFactory.create_llm(
        model_name=reasoning_model or configurable.reflection_model,
        temperature=1.0,
        max_retries=2,
    )
    result = llm.invoke(formatted_prompt)
    
    # Extract content and parse response
    if hasattr(result, 'content'):
        content = result.content
    else:
        content = str(result)
    
    # Parse the JSON response
    is_sufficient = False
    knowledge_gap = ""
    follow_up_queries = []
    
    try:
        import json
        import re
        
        # Try to extract JSON from the response
        # Look for JSON block between ```json and ```
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            # Try to parse the entire content as JSON
            json_content = content
        
        # Parse JSON
        parsed_json = json.loads(json_content)
        
        # Extract values from the parsed JSON
        is_sufficient = parsed_json.get('is_sufficient', False)
        knowledge_gap = parsed_json.get('knowledge_gap', '')
        follow_up_queries = parsed_json.get('follow_up_queries', [])
        
        # Ensure follow_up_queries is a list
        if isinstance(follow_up_queries, str):
            follow_up_queries = [follow_up_queries]
        elif not isinstance(follow_up_queries, list):
            follow_up_queries = []
        
        print(f"DEBUG: reflection parsed JSON successfully: {parsed_json}")
        
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        print(f"DEBUG: JSON parsing failed: {e}")
        print(f"DEBUG: Raw content: {content}")
        # Fallback to original text parsing
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.upper().startswith('SUFFICIENT:') or line.upper().startswith('1.'):
                is_sufficient = 'yes' in line.lower() or 'true' in line.lower()
            elif line.upper().startswith('KNOWLEDGE_GAP:') or line.upper().startswith('2.'):
                knowledge_gap = line.split(':', 1)[-1].strip()
            elif line.upper().startswith('FOLLOW_UP_QUERIES:') or line.upper().startswith('3.'):
                # Extract follow-up queries
                query_text = line.split(':', 1)[-1].strip()
                if query_text and query_text != '[list of queries if not sufficient]':
                    follow_up_queries = [q.strip() for q in query_text.split(',') if q.strip()]
            elif line and not any(x in line.upper() for x in ['SUFFICIENT', 'KNOWLEDGE_GAP', 'FOLLOW_UP']):
                # Additional follow-up queries on separate lines
                if line.startswith('-') or line.startswith('•') or line[0].isdigit():
                    query = line.lstrip('-•0123456789. ').strip()
                    if query and isinstance(follow_up_queries, list):
                        follow_up_queries.append(query)

    search_query = state.get("search_query", [])
    query_count = len(search_query) if search_query else 0
    
    # Debug output
    print(f"DEBUG: reflection follow_up_queries: {follow_up_queries}")
    print(f"DEBUG: reflection is_sufficient: {is_sufficient}")
    
    return {
        "is_sufficient": is_sufficient,
        "knowledge_gap": knowledge_gap,
        "follow_up_queries": follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": query_count,
    }


def evaluate_research(state: ReflectionState, config: RunnableConfig) -> str:
    """LangGraph routing function that determines the next step in the research flow."""
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    
    research_loop_count = state.get("research_loop_count", 0) or 0
    max_loops = max_research_loops if max_research_loops is not None else 3
    
    if state.get("is_sufficient", False) or (research_loop_count >= max_loops):
        return "finalize_answer"
    else:
        return "continue_research"


def continue_research(state: OverallState) -> Dict[str, Any]:
    """Continue research with follow-up queries."""
    # Get follow-up queries from reflection state
    follow_up_queries = state.get("follow_up_queries", [])
    
    # If there are no follow-up queries, return empty update
    if not follow_up_queries:
        return {}
    
    # Use the first follow-up query for the next research iteration
    next_query = follow_up_queries[0]
    
    # Debug output
    print(f"DEBUG: continue_research using next_query: {next_query}")
    
    return {
        "search_query": [next_query],  # Ensure it's a list for consistency
        "follow_up_queries": follow_up_queries[1:],  # Remove the used query
    }


def finalize_answer(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """LangGraph node that finalizes the research summary."""
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model

    # Combine RAG documents with web research results
    all_summaries = []
    
    # Add RAG documents if available with clear labeling
    rag_documents = state.get("rag_documents")
    if rag_documents:
        print(f"DEBUG: Adding {len(rag_documents)} RAG documents to final answer")
        for i, doc in enumerate(rag_documents):
            labeled_doc = f"=== KNOWLEDGE BASE SOURCE {i+1} ===\n{doc}\n=== END KNOWLEDGE BASE SOURCE {i+1} ==="
            all_summaries.append(labeled_doc)
    else:
        print("DEBUG: No RAG documents available for final answer")
    
    # Add web research results with clear labeling
    web_research_result = state.get("web_research_result")
    if web_research_result:
        print(f"DEBUG: Adding {len(web_research_result)} web research results to final answer")
        for i, result in enumerate(web_research_result):
            labeled_result = f"=== WEB RESEARCH SOURCE {i+1} ===\n{result}\n=== END WEB RESEARCH SOURCE {i+1} ==="
            all_summaries.append(labeled_result)
    else:
        print("DEBUG: No web research results available for final answer")

    # Format the prompt
    current_date = get_current_date()
    summaries_text = "\n\n".join(all_summaries) if all_summaries else "No research content available."
    
    print(f"DEBUG: Total sources for final answer: {len(all_summaries)}")
    print(f"DEBUG: Summary text length: {len(summaries_text)} characters")
    
    # Safely get research topic from messages
    messages = state.get("messages", [])
    if not messages:
        research_topic = "General research topic"
    else:
        research_topic = get_research_topic(messages)
    
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=research_topic,
        summaries=summaries_text,
    )

    # init Reasoning Model
    llm = LLMFactory.create_llm(
        model_name=reasoning_model or configurable.answer_model,
        temperature=0,
        max_retries=2,
    )
    
    result = llm.invoke(formatted_prompt)
    
    # Extract content from the response
    if hasattr(result, 'content'):
        final_answer = result.content
        # 多轮对话确保大模型输出完整而非因为长度截断
        finish_reason = result.response_metadata["finish_reason"]
        # responseid = result.id #豆包大模型多轮对话需要
        while finish_reason == "length": # 如果正常结束该值为stop
            print(f"发现未完待续，续写 ...")
            # continuation = llm.invoke([HumanMessage("请继续上文接着写")], previous_response_id=responseid) #豆包大模型多轮对话需要
            continuation = llm.invoke("请继续上文接着写，\n 上文：" + final_answer)
            final_answer = final_answer + "\n" + continuation.content
            finish_reason = continuation.response_metadata["finish_reason"]
            # responseid = continuation.id #豆包大模型多轮对话需要
            time.sleep(2)  # 避免 API 限速
    else:
        final_answer = str(result)

    return {
        "messages": [
            AIMessage(content=final_answer)
        ]
    }


# Build the graph
def build_graph():
    """Build the LangGraph research agent."""
    # Import RAG functions locally to avoid circular imports
    from rag_nodes import rag_retrieve, should_use_rag, rag_fallback_to_web
    
    workflow = StateGraph(OverallState)

    # Add nodes
    workflow.add_node("generate_query", generate_query)
    workflow.add_node("web_research", web_research)
    workflow.add_node("reflection", reflection)
    workflow.add_node("continue_research", continue_research)
    workflow.add_node("finalize_answer", finalize_answer)
    workflow.add_node("rag_retrieve", rag_retrieve)

    # Add edges - Enhanced RAG integration
    workflow.add_edge(START, "generate_query")
    
    # Route to RAG or web research based on configuration
    workflow.add_conditional_edges(
        "generate_query",
        should_use_rag,
        {
            "rag_retrieve": "rag_retrieve",
            "web_research": "web_research",
        }
    )
    
    # After RAG retrieval, decide whether to fallback to web research
    workflow.add_conditional_edges(
        "rag_retrieve",
        rag_fallback_to_web,
        {
            "web_research": "web_research", 
            "reflection": "reflection",
        }
    )
    
    # Web research always goes to reflection
    workflow.add_edge("web_research", "reflection")
    
    # Reflection decides whether to continue research or finalize
    workflow.add_conditional_edges(
        "reflection",
        evaluate_research,
        {
            "finalize_answer": "finalize_answer",
            "continue_research": "continue_research",
        }
    )
    
    # Continue research goes back to web research (not RAG, to avoid loops)
    workflow.add_conditional_edges(
        "continue_research",
        should_use_rag,
        {
            "rag_retrieve": "rag_retrieve",
            "web_research": "web_research",
        }
    )
    
    workflow.add_edge("finalize_answer", END)

    return workflow.compile()


# Create the compiled graph
research_graph = build_graph() 
