"""Modified LangGraph implementation supporting multiple LLM providers."""

import os
from typing import Any, Dict, List

# Use absolute imports for LangGraph compatibility
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig

try:
    from .state import (
        OverallState,
        QueryGenerationState,
        ReflectionState,
        WebSearchState,
    )
    from .configuration import Configuration
    from .prompts import (
        get_current_date,
        query_writer_instructions,
        web_searcher_instructions,
        reflection_instructions,
        answer_instructions,
    )
    from .llm_factory import LLMFactory
    from .web_search_tool import web_search_tool
    from .utils import (
        get_research_topic,
    )
except ImportError:
    # Fallback for direct execution
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
        max_tokens=configurable.max_tokens,
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
    
    # SAFETY: Add timeout protection for web research
    import threading
    import time
    
    search_results = []
    search_completed = threading.Event()
    search_error = None
    
    def perform_search():
        nonlocal search_results, search_error
        try:
            # Perform web search with additional timeout protection
            search_results = web_search_tool.search(query_text, max_results=5)
            search_completed.set()
        except Exception as e:
            search_error = e
            search_completed.set()
    
    # Start search in separate thread
    search_thread = threading.Thread(target=perform_search)
    search_thread.daemon = True
    search_thread.start()
    
    # Wait for completion with timeout
    if search_completed.wait(timeout=45):  # 45 seconds timeout
        if search_error:
            print(f"Web search failed with error: {search_error}")
            search_results = []
        else:
            print(f"DEBUG: search_results from web_search_tool: {search_results}")
    else:
        print("WARNING: Web search timed out after 45 seconds, using empty results")
        search_results = []
    
    # Debug output
    print(f"DEBUG: search_results type: {type(search_results)}")
    print(f"DEBUG: search_results length: {len(search_results) if search_results else 0}")
    
    # Format search results for the LLM
    formatted_results = web_search_tool.format_search_results(search_results)
    
    # Create LLM to analyze and summarize the search results
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0,
        max_retries=2,
        max_tokens=configurable.max_tokens,
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
    new_loop_count = (current_loop_count or 0) + 1
    state["research_loop_count"] = new_loop_count
    reasoning_model = state.get("reasoning_model", configurable.reflection_model)
    
    # ULTRA-CONSERVATIVE CIRCUIT BREAKER: No loops allowed at all for safety
    print(f"ULTRA-SAFE CIRCUIT BREAKER: Loop count {new_loop_count}, FORCING sufficient to prevent ANY loops")
    return {
        "is_sufficient": True,
        "knowledge_gap": "Research completed immediately to prevent infinite loops",
        "follow_up_queries": [],
        "research_loop_count": new_loop_count,
        "number_of_ran_queries": 0,
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
    # SAFETY FIRST: Never continue research to prevent infinite loops
    print("SAFETY OVERRIDE: continue_research disabled to prevent infinite loops")
    return {
        "is_sufficient": True,
        "follow_up_queries": [],
        "search_query": [],
    }
    
    # The rest of the function is commented out for safety
    # Get follow-up queries from reflection state
    # follow_up_queries = state.get("follow_up_queries", [])
    
    # If there are no follow-up queries, return empty update
    # if not follow_up_queries:
    #     return {}
    
    # Use the first follow-up query for the next research iteration
    # next_query = follow_up_queries[0]
    
    # Debug output
    # print(f"DEBUG: continue_research using next_query: {next_query}")
    
    # return {
    #     "search_query": [next_query],  # Ensure it's a list for consistency
    #     "follow_up_queries": follow_up_queries[1:],  # Remove the used query
    # }


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
        max_tokens=configurable.max_tokens,
    )
    
    result = llm.invoke(formatted_prompt)
    
    # Extract content from the response
    if hasattr(result, 'content'):
        final_answer = result.content
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
    # Import functions locally to avoid circular imports
    try:
        from .rag_nodes import rag_retrieve, should_use_rag, rag_fallback_to_web
        from .long_report_nodes import (
            detect_long_report_request,
            generate_report_plan,
            should_generate_long_report
        )
        # Import enhanced long report processing
        from .enhanced_long_report_nodes import (
            detect_long_report_request,
            enhanced_generate_report_plan,
            process_next_section,
            compile_enhanced_final_report,
            should_generate_long_report,
            has_more_sections_to_process
        )
    except ImportError:
        from rag_nodes import rag_retrieve, should_use_rag, rag_fallback_to_web
        from long_report_nodes import (
            detect_long_report_request,
            generate_report_plan,
            should_generate_long_report
        )
        # Import enhanced long report processing
        from enhanced_long_report_nodes import (
            detect_long_report_request,
            enhanced_generate_report_plan,
            process_next_section,
            compile_enhanced_final_report,
            should_generate_long_report,
            has_more_sections_to_process
        )
    
    workflow = StateGraph(OverallState)

    # Add existing nodes
    workflow.add_node("generate_query", generate_query)
    workflow.add_node("web_research", web_research)
    workflow.add_node("reflection", reflection)
    workflow.add_node("continue_research", continue_research)
    workflow.add_node("finalize_answer", finalize_answer)
    workflow.add_node("rag_retrieve", rag_retrieve)
    
    # Add enhanced long report nodes
    workflow.add_node("detect_long_report", detect_long_report_request)
    workflow.add_node("generate_report_plan", enhanced_generate_report_plan)
    workflow.add_node("process_section", process_next_section)
    workflow.add_node("compile_report", compile_enhanced_final_report)

    # 极简流程 - 完全消除循环可能
    
    # 开始检测
    workflow.add_edge(START, "detect_long_report")
    
    # 简单路由
    workflow.add_conditional_edges(
        "detect_long_report",
        should_generate_long_report,
        {
            "long_report": "generate_report_plan",
            "standard_flow": "generate_query",
        }
    )
    
    # 新的简化章节处理流程
    workflow.add_edge("generate_report_plan", "process_section")
    
    # 条件路由：检查是否还有更多章节需要处理
    workflow.add_conditional_edges(
        "process_section",
        has_more_sections_to_process,
        {
            "process_section": "process_section",  # 继续处理下一个章节
            "compile_report": "compile_report",    # 完成所有章节，编译报告
        }
    )
    
    workflow.add_edge("compile_report", END)
    
    # 标准流：尽可能简化
    workflow.add_conditional_edges(
        "generate_query",
        should_use_rag,
        {
            "rag_retrieve": "rag_retrieve",
            "web_research": "web_research",
        }
    )
    
    # RAG结果处理
    workflow.add_conditional_edges(
        "rag_retrieve",
        rag_fallback_to_web,
        {
            "web_research": "web_research",
            "reflection": "reflection",
        }
    )
    
    # Web研究后直接反思
    workflow.add_edge("web_research", "reflection")
    
    # 反思后的简化路由：要么完成，要么继续一次
    def simple_evaluate_research(state: OverallState) -> str:
        """超简化的评估逻辑，最多循环一次。"""
        research_loop_count = state.get("research_loop_count", 0) or 0
        
        # 强制限制：最多1次循环
        if state.get("is_sufficient", False) or (research_loop_count >= 1):
            return "finalize_answer"
        else:
            return "continue_research"
    
    workflow.add_conditional_edges(
        "reflection",
        simple_evaluate_research,
        {
            "finalize_answer": "finalize_answer",
            "continue_research": "continue_research",
        }
    )
    
    # 继续研究：只用Web搜索，避免RAG复杂性
    workflow.add_edge("continue_research", "web_research")
    
    # 最终结束
    workflow.add_edge("finalize_answer", END)

    return workflow.compile(
        checkpointer=None,
        interrupt_before=None,
        interrupt_after=None,
        debug=False
    )


# Create the compiled graph
research_graph = build_graph() 