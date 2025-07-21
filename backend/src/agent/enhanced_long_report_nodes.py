"""
Enhanced long report generation with simplified chapter-by-chapter processing.
This module provides improved long report generation without complex subgraph structures.
"""

import logging
import sys
import os
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Use absolute imports for LangGraph compatibility
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .state import OverallState, ReportPlan, ReportSection
    from .configuration import Configuration
    from .llm_factory import LLMFactory
    from .web_search_tool import web_search_tool
    from .utils import get_research_topic
    from .rag_nodes import rag_retrieve
    from .prompts import get_current_date
except ImportError:
    # Fallback for direct execution
    from state import OverallState, ReportPlan, ReportSection
    from configuration import Configuration
    from llm_factory import LLMFactory
    from web_search_tool import web_search_tool
    from utils import get_research_topic
    from rag_nodes import rag_retrieve
    from prompts import get_current_date

logger = logging.getLogger(__name__)


def detect_long_report_request(state: OverallState) -> Dict[str, Any]:
    """Detect if the user is requesting a long report."""
    messages = state.get("messages", [])
    if not messages:
        return {"is_long_report": False}
    
    # Get the latest user message
    latest_message = messages[-1]
    content = latest_message.content if hasattr(latest_message, 'content') else str(latest_message)
    
    # Ensure content is a string
    if isinstance(content, list):
        content = " ".join(str(item) for item in content)
    elif not isinstance(content, str):
        content = str(content)
    
    # Keywords that indicate long report request
    long_report_keywords = [
        "详细报告", "研究报告", "深度分析", "全面报告", "长篇报告",
        "detailed report", "research report", "comprehensive analysis",
        "in-depth report", "long report", "万字", "字的报告"
    ]
    
    # Word count indicators
    word_count_indicators = ["万字", "千字", "words", "字"]
    
    is_long_report = any(keyword in content.lower() for keyword in long_report_keywords)
    has_word_count = any(indicator in content for indicator in word_count_indicators)
    
    # If it's a long report request, extract target word count
    target_word_count = 10000  # Default 10k words
    if has_word_count:
        import re
        # Try to extract number + 万字 pattern
        wan_pattern = r'(\d+)万字'
        wan_match = re.search(wan_pattern, content)
        if wan_match:
            target_word_count = int(wan_match.group(1)) * 10000
        
        # Try to extract number + 千字 pattern
        qian_pattern = r'(\d+)千字'
        qian_match = re.search(qian_pattern, content)
        if qian_match:
            target_word_count = int(qian_match.group(1)) * 1000
        
        # Try to extract number + words pattern
        words_pattern = r'(\d+)\s*words'
        words_match = re.search(words_pattern, content.lower())
        if words_match:
            target_word_count = int(words_match.group(1))
    
    result = {
        "is_long_report": is_long_report or has_word_count,
        "target_word_count": target_word_count
    }
    
    logger.info(f"Long report detection: {result['is_long_report']}, target words: {result['target_word_count']}")
    
    return result


def enhanced_generate_report_plan(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate a detailed plan for the long report with enhanced section information."""
    configurable = Configuration.from_runnable_config(config)
    
    messages = state.get("messages", [])
    research_topic = get_research_topic(messages)
    # 确保使用detect_long_report_request检测到的字数，如果没有则默认10000
    target_word_count = state.get("target_word_count", 10000)
    
    logger.info(f"Generating report plan with target word count: {target_word_count}")
    
    # Create LLM for planning
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0.7,
        max_retries=2,
        max_tokens=configurable.max_tokens,
    )
    
    # Create planning prompt
    planning_prompt = f"""你是一个专业的研究报告规划师。请为以下研究主题创建一个详细的报告计划：

研究主题：{research_topic}
目标字数：{target_word_count}字

请生成一个包含以下信息的报告计划：
1. 报告标题
2. 报告摘要（200字左右）
3. 详细的章节规划，每个章节包括：
   - 章节名称
   - 章节描述（该章节应该覆盖的内容）
   - 是否需要研究（true/false）
   - 目标字数

要求：
- 报告应该逻辑清晰，结构完整
- 章节数量应该足够支撑目标字数（{target_word_count}字建议6-10个章节）
- 需要研究的章节应该标记为requires_research: true
- 【关键】总字数必须达到目标字数，各章节字数分配总和应等于目标字数
- 每个章节的字数分配要合理，主要章节应该有足够的字数（1500-4000字）
- 确保所有章节的word_count_target总和等于{target_word_count}

请以JSON格式输出，格式如下：
{{
    "title": "报告标题",
    "abstract": "报告摘要",
    "total_word_count_target": {target_word_count},
    "sections": [
        {{
            "name": "章节名称",
            "description": "章节描述",
            "requires_research": true,
            "word_count_target": 1500
        }}
    ]
}}"""

    # Generate plan
    result = llm.invoke([SystemMessage(content=planning_prompt)])
    
    # Extract and parse the plan
    content = result.content if hasattr(result, 'content') else str(result)
    
    try:
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
        
        plan_data = json.loads(json_content)
        
        # Create ReportPlan object
        sections = [
            ReportSection(
                name=section["name"],
                description=section["description"],
                requires_research=section.get("requires_research", True),
                word_count_target=section.get("word_count_target", 1000)
            )
            for section in plan_data["sections"]
        ]
        
        report_plan = ReportPlan(
            title=plan_data["title"],
            abstract=plan_data["abstract"],
            sections=sections,
            total_word_count_target=plan_data.get("total_word_count_target", target_word_count)
        )
        
        logger.info(f"Generated report plan with {len(sections)} sections")
        
        return {
            "report_plan": report_plan,
            "current_section_index": 0,
            "completed_sections": [],
            "sections_completed_count": 0,  # Initialize completed count
            "total_sections": len(sections),  # Initialize total sections for frontend
            "next_section_index": None,  # No next section initially
            # Send generate_report_plan event to frontend
            "generate_report_plan": {
                "report_plan": report_plan
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to parse report plan: {e}")
        # Fallback to a simple plan with proper word distribution
        # Ensure target_word_count is not None
        safe_target_count = target_word_count or 10000
        fallback_sections = [
            ReportSection(
                name="引言",
                description="介绍研究背景和目标",
                requires_research=True,
                word_count_target=safe_target_count // 5  # 20%
            ),
            ReportSection(
                name="文献综述",
                description="相关研究和理论基础",
                requires_research=True,
                word_count_target=safe_target_count * 3 // 10  # 30%
            ),
            ReportSection(
                name="核心分析",
                description="主要内容分析",
                requires_research=True,
                word_count_target=safe_target_count * 35 // 100  # 35%
            ),
            ReportSection(
                name="总结",
                description="总结要点和结论",
                requires_research=False,
                word_count_target=safe_target_count * 15 // 100  # 15%
            ),
        ]
        
        fallback_plan = ReportPlan(
            title=f"{research_topic}研究报告",
            abstract=f"本报告针对{research_topic}进行深入研究和分析。",
            sections=fallback_sections,
            total_word_count_target=safe_target_count
        )
        
        return {
            "report_plan": fallback_plan,
            "current_section_index": 0,
            "completed_sections": [],
            "sections_completed_count": 0,  # Initialize completed count
            "total_sections": len(fallback_sections),  # Initialize total sections for frontend
            "next_section_index": None,  # No next section initially
            # Send generate_report_plan event to frontend
            "generate_report_plan": {
                "report_plan": fallback_plan
            }
        }


def process_next_section(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Process the next section in the report plan."""
    configurable = Configuration.from_runnable_config(config)
    report_plan = state.get("report_plan")
    
    # Use next_section_index if available (for subsequent iterations), otherwise use current_section_index
    next_section_index = state.get("next_section_index")
    if next_section_index is not None:
        section_index_to_process = next_section_index
        logger.info(f"Using next_section_index for processing: {next_section_index}")
    else:
        section_index_to_process = state.get("current_section_index", 0)
        logger.info(f"Using current_section_index for processing: {section_index_to_process}")
    
    completed_sections = list(state.get("completed_sections", []))  # Create a new list to avoid mutation issues
    
    logger.info(f"Processing: section_index_to_process={section_index_to_process}, completed_sections_count={len(completed_sections)}")
    
    if not report_plan or section_index_to_process >= len(report_plan.sections):
        logger.info("No more sections to process")
        return {"processing_complete": True}
    
    current_section = report_plan.sections[section_index_to_process]
    logger.info(f"Processing section {section_index_to_process + 1}/{len(report_plan.sections)}: {current_section.name}")
    
    # Process the section content
    if not current_section.requires_research:
        # Generate content without research for sections like intro/conclusion
        content = generate_non_research_section_content(current_section, state, config)
        current_section.content = content
        current_section.completed = True
        completed_sections.append(current_section)
    else:
        # Process research-based section
        # Step 1: Generate research queries
        queries = generate_section_research_queries(current_section, state, config)
        
        # Step 2: Perform research (RAG + Web)
        logger.info(f"Starting research for section: {current_section.name}")
        research_content = perform_section_research(queries, state, config)
        
        # Step 3: Generate section content  
        logger.info(f"Generating content for section: {current_section.name}")
        content = generate_section_content_from_research(current_section, research_content, state, config)
        
        # Update section
        current_section.content = content
        current_section.completed = True
        completed_sections.append(current_section)
    
    logger.info(f"Completed section: {current_section.name}")
    
    # Calculate progress AFTER completing the section
    sections_completed_count = len(completed_sections)
    next_section_index = section_index_to_process + 1  # Index for the next iteration
    
    logger.info(f"State update: section_index_to_process={section_index_to_process} -> {next_section_index}, completed_count={sections_completed_count}")
    
    # CRITICAL FIX: Frontend expects current_section_index to be the section JUST COMPLETED for display
    # So we should send the index of the section we just finished, not the next one
    result_update = {
        "current_section_index": section_index_to_process,  # The section we just completed
        "next_section_index": next_section_index,  # For internal state tracking
        "sections_completed_count": sections_completed_count,  # Updated count
        "completed_sections": completed_sections,  # Updated list
        # Info for frontend display about the section we just completed
        "section_name": current_section.name,
        "section_description": current_section.description,
        "total_sections": len(report_plan.sections)
    }
    
    logger.info(f"Sending to frontend: Section {section_index_to_process + 1}/{len(report_plan.sections)}: {current_section.name}")
    logger.info(f"Frontend will display: Completed: {sections_completed_count}/{len(report_plan.sections)} sections")
    
    # CRITICAL: Send process_section event to frontend
    # The event key must match what frontend expects
    return {
        **result_update,  # Include all state updates
        "process_section": {  # This is the event key that frontend listens for
            "current_section_index": section_index_to_process,
            "total_sections": len(report_plan.sections),
            "sections_completed_count": sections_completed_count,
            "section_name": current_section.name,
            "section_description": current_section.description
        }
    }


def generate_section_research_queries(section: ReportSection, state: OverallState, config: RunnableConfig) -> List[str]:
    """Generate research queries for a specific section."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0.8,
        max_retries=2,
        max_tokens=configurable.max_tokens,
    )
    
    query_prompt = f"""你是一个专业的研究分析师，正在为一个报告章节生成研究查询。

章节信息：
标题：{section.name}
描述：{section.description}
目标字数：{section.word_count_target}

你的任务是为这个章节生成3-5个高质量的研究查询，这些查询应该：
1. 直接相关于章节主题
2. 能够帮助收集编写此章节所需的信息
3. 涵盖章节的不同方面
4. 具体且有针对性

请生成查询列表，每个查询一行，不需要编号。

当前日期：{get_current_date()}
"""
    
    result = llm.invoke([SystemMessage(content=query_prompt)])
    content = result.content if hasattr(result, 'content') else str(result)
    
    # Parse queries
    queries = []
    for line in content.strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove numbering and bullet points
            line = line.lstrip('0123456789.-• ')
            if line:
                queries.append(line)
    
    # Ensure we have at least one query
    if not queries:
        queries = [f"{section.name} {section.description}"]
    
    logger.info(f"Generated {len(queries)} queries for section: {section.name}")
    return queries[:5]  # Limit to 5 queries


def perform_section_research(queries: List[str], state: OverallState, config: RunnableConfig) -> List[str]:
    """Perform research using both RAG and web search."""
    research_content = []
    
    # Try RAG first if enabled
    if state.get("rag_enabled", False) and state.get("rag_resources"):
        try:
            # Convert queries to a format suitable for RAG
            for query in queries:
                rag_state = {
                    "messages": [{"role": "user", "content": query}],
                    "rag_resources": state.get("rag_resources", []),
                    "rag_enabled": True
                }
                rag_result = rag_retrieve(rag_state, config)
                rag_documents = rag_result.get("rag_documents", [])
                research_content.extend(rag_documents)
        except Exception as e:
            logger.error(f"RAG research failed: {e}")
    
    # Perform web search using the correct method
    for query in queries:
        try:
            # Use the correct search method
            search_results = web_search_tool.search(query, max_results=3)
            if search_results:
                # Format the results into readable text
                formatted_results = web_search_tool.format_search_results(search_results)
                research_content.append(formatted_results)
                logger.info(f"Web search successful for query: {query[:50]}...")
            else:
                logger.warning(f"No search results for query: {query[:50]}...")
        except Exception as e:
            logger.error(f"Web search failed for query '{query}': {e}")
            continue
    
    logger.info(f"Collected {len(research_content)} research results")
    return research_content


def generate_section_content_from_research(section: ReportSection, research_content: List[str], state: OverallState, config: RunnableConfig) -> str:
    """Generate section content based on research results."""
    configurable = Configuration.from_runnable_config(config)
    
    # Use higher token limit for long report sections
    section_max_tokens = min(configurable.max_tokens * 2, 16384)  # Double tokens for long content
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0.7,
        max_retries=2,
        max_tokens=section_max_tokens,
    )
    
    # Prepare content for writing
    content_text = "\n\n".join(research_content) if research_content else ""
    
    writing_prompt = f"""你是一个专业的研究报告撰写专家，正在为一个长报告编写特定章节的内容。

章节信息：
标题：{section.name}
描述：{section.description}
目标字数：{section.word_count_target}字 （必须达到此字数要求！）

研究资料：
{content_text[:8000]}...

请基于提供的研究资料编写这个章节的内容。要求：

1. 内容结构：
   - 使用 ## {section.name} 作为章节标题
   - 合理分段，每段3-5句话
   - 逻辑清晰，层次分明
   - 使用多级标题（###、####）来组织内容

2. 写作要求：
   - 【关键要求】内容必须达到 {section.word_count_target} 字，不能少于此数字！
   - 语言专业且易懂，内容详实丰富
   - 基于研究资料，包含深入分析和见解
   - 包含具体的数据、案例、例子或分析
   - 如字数不够，请增加更多子主题、详细阐述、案例分析等

3. 内容深度：
   - 对每个要点进行详细阐述
   - 提供具体例子和数据支撑
   - 分析不同观点和角度
   - 包含前因后果的分析

4. 引用要求：
   - 在相关内容后添加 [1]、[2] 等引用标记
   - 在章节末尾添加 ### 参考资料 部分
   - 列出具体的来源信息

请直接输出章节内容，确保内容丰富且达到指定字数要求。
"""
    
    result = llm.invoke([SystemMessage(content=writing_prompt)])
    return result.content if hasattr(result, 'content') else str(result)


def generate_non_research_section_content(section: ReportSection, state: OverallState, config: RunnableConfig) -> str:
    """Generate content for sections that don't require research (like intro/conclusion)."""
    configurable = Configuration.from_runnable_config(config)
    
    # Use higher token limit for long report sections
    section_max_tokens = min(configurable.max_tokens * 2, 16384)  # Double tokens for long content
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0.7,
        max_retries=2,
        max_tokens=section_max_tokens,
    )
    
    report_plan = state.get("report_plan")
    completed_sections = state.get("completed_sections", [])
    
    # Create context from completed sections if this is a conclusion
    context = ""
    if "总结" in section.name or "结论" in section.name or "conclusion" in section.name.lower():
        context = "\n\n".join([s.content for s in completed_sections if s.content])[:2000]
    
    writing_prompt = f"""你是一个专业的研究报告撰写专家。请为以下章节撰写内容：

报告标题：{report_plan.title if report_plan else "研究报告"}
章节名称：{section.name}
章节描述：{section.description}
目标字数：{section.word_count_target}字 （必须达到此字数要求！）

{f"已完成章节内容参考：{context}" if context else ""}

请基于章节描述生成专业的内容。要求：
1. 使用 ## {section.name} 作为标题
2. 【关键要求】内容必须达到 {section.word_count_target} 字，不能少于此数字！
3. 内容专业、准确、有条理，详实丰富
4. 使用多级标题（###、####）来组织内容
5. 如果是总结章节，请基于已完成的章节内容进行详细总结
6. 包含具体的论述、分析、见解，不要只是简单列举

内容深度要求：
- 对每个要点进行详细阐述和分析
- 提供具体例子、数据或案例
- 分析不同角度和层面
- 如字数不够，请增加更多子主题和详细说明

请直接输出章节内容，确保内容丰富且达到指定字数要求。
"""
    
    result = llm.invoke([SystemMessage(content=writing_prompt)])
    return result.content if hasattr(result, 'content') else str(result)


def compile_enhanced_final_report(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Compile the final report from all completed sections."""
    report_plan = state.get("report_plan")
    completed_sections = state.get("completed_sections", [])
    
    if not report_plan:
        logger.error("No report plan found")
        return {
            "messages": [AIMessage(content="报告生成失败：缺少报告计划")],
            "processing_complete": True
        }
    
    # Build the final report
    final_report_parts = []
    
    # Add title and abstract
    final_report_parts.append(f"# {report_plan.title}\n")
    final_report_parts.append(f"## 摘要\n{report_plan.abstract}\n")
    
    # Add all sections in order
    for section in completed_sections:
        if section.content:
            final_report_parts.append(section.content)
    
    final_report = "\n\n".join(final_report_parts)
    
    logger.info(f"Compiled final report with {len(final_report)} characters")
    
    # CRITICAL FIX: Only send the final complete report as a single message
    # Remove any intermediate content that might have accumulated
    return {
        "final_report": final_report,
        "messages": [AIMessage(content=final_report)],  # Only the final report
        "processing_complete": True
    }


def should_generate_long_report(state: OverallState) -> str:
    """Route based on long report detection."""
    if state.get("is_long_report", False):
        return "long_report"
    else:
        return "standard_flow"


def has_more_sections_to_process(state: OverallState) -> str:
    """Check if there are more sections to process."""
    if state.get("processing_complete", False):
        logger.info("Processing marked as complete, compiling report")
        return "compile_report"
    
    report_plan = state.get("report_plan")
    # Use next_section_index for routing if available, otherwise use current_section_index
    next_section_index = state.get("next_section_index")
    if next_section_index is not None:
        section_index_to_check = next_section_index
        logger.info(f"Using next_section_index for routing: {next_section_index}")
    else:
        section_index_to_check = state.get("current_section_index", 0)
        logger.info(f"Using current_section_index for routing: {section_index_to_check}")
    
    total_sections = len(report_plan.sections) if report_plan else 0
    completed_count = len(state.get("completed_sections", []))
    
    logger.info(f"Routing check: section_index_to_check={section_index_to_check}, total_sections={total_sections}, completed_count={completed_count}")
    
    if not report_plan or section_index_to_check >= total_sections:
        logger.info(f"No more sections to process (index: {section_index_to_check}, total: {total_sections})")
        return "compile_report"
    else:
        logger.info(f"Continue processing section {section_index_to_check + 1}/{total_sections}")
        return "process_section" 