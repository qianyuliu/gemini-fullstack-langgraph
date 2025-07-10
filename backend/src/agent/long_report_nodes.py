"""Long report generation nodes for the LangGraph agent."""

import logging
import sys
import os
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

# Use absolute imports for LangGraph compatibility
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .state import OverallState, ReportPlan, ReportSection, SectionGenerationResult
    from .configuration import Configuration
    from .llm_factory import LLMFactory
    from .utils import get_research_topic
except ImportError:
    # Fallback for direct execution
    from state import OverallState, ReportPlan, ReportSection, SectionGenerationResult
    from configuration import Configuration
    from llm_factory import LLMFactory
    from utils import get_research_topic

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
    
    logger.info(f"Long report detection: {is_long_report or has_word_count}, target words: {target_word_count}")
    
    return {
        "is_long_report": is_long_report or has_word_count,
        "target_word_count": target_word_count
    }


def generate_report_plan(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate a detailed plan for the long report."""
    configurable = Configuration.from_runnable_config(config)
    
    messages = state.get("messages", [])
    research_topic = get_research_topic(messages)
    target_word_count = state.get("target_word_count", 10000)
    
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
- 章节数量应该合理（建议5-8个章节）
- 需要研究的章节应该标记为requires_research: true
- 总字数应该接近目标字数
- 每个章节的字数分配要合理

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
        
        return {"report_plan": report_plan}
        
    except Exception as e:
        logger.error(f"Failed to parse report plan: {e}")
        # Fallback to a simple plan
        fallback_sections = [
            ReportSection(
                name="引言",
                description="介绍研究背景和目标",
                requires_research=True,
                word_count_target=target_word_count // 6
            ),
            ReportSection(
                name="文献综述",
                description="相关研究和理论基础",
                requires_research=True,
                word_count_target=target_word_count // 4
            ),
            ReportSection(
                name="核心分析",
                description="主要内容分析",
                requires_research=True,
                word_count_target=target_word_count // 3
            ),
            ReportSection(
                name="结论",
                description="总结和建议",
                requires_research=False,
                word_count_target=target_word_count // 6
            )
        ]
        
        fallback_plan = ReportPlan(
            title=f"{research_topic}研究报告",
            abstract=f"关于{research_topic}的详细研究报告",
            sections=fallback_sections,
            total_word_count_target=target_word_count
        )
        
        return {"report_plan": fallback_plan}


def generate_section_queries(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Generate specific research queries for a section."""
    configurable = Configuration.from_runnable_config(config)
    
    current_section = state["current_section"]
    if not current_section or not current_section.requires_research:
        return {"search_query": []}
    
    # Create LLM for query generation
    llm = LLMFactory.create_llm(
        model_name=configurable.query_generator_model,
        temperature=0.8,
        max_retries=2,
        max_tokens=configurable.max_tokens,
    )
    
    # Create query generation prompt
    query_prompt = f"""请为以下报告章节生成2个最有效的搜索查询：

章节名称：{current_section.name}
章节描述：{current_section.description}
目标字数：{current_section.word_count_target}字

要求：
- 查询应该具体且有针对性，避免泛泛而谈
- 每个查询应该覆盖不同的信息维度
- 查询要有区分度，避免重复
- 优先考虑能获得高质量信息的查询
- 适合网络搜索和知识库检索

请以JSON格式输出2个精选查询：
{{
    "queries": ["精确查询1", "精确查询2"]
}}"""

    result = llm.invoke([SystemMessage(content=query_prompt)])
    content = result.content if hasattr(result, 'content') else str(result)
    
    try:
        import json
        import re
        
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
        
        query_data = json.loads(json_content)
        queries = query_data.get("queries", [])
        
        # Deduplicate and limit queries to reduce redundant searches
        seen_queries = set()
        unique_queries = []
        for query in queries:
            query_lower = query.lower().strip()
            if query_lower not in seen_queries and len(query_lower) > 5:
                seen_queries.add(query_lower)
                unique_queries.append(query)
        
        # Limit to 2 queries maximum to reduce redundancy
        unique_queries = unique_queries[:2]
        
        logger.info(f"Generated {len(unique_queries)} unique queries for section '{current_section.name}': {unique_queries}")
        
        # Add to global query history to avoid duplicates
        executed_queries = state.get("executed_queries", set())
        if isinstance(executed_queries, list):
            executed_queries = set(executed_queries)
        
        # Filter out already executed queries
        final_queries = []
        for query in unique_queries:
            query_key = query.lower().strip()
            if query_key not in executed_queries:
                final_queries.append(query)
                executed_queries.add(query_key)
        
        # If no new queries, create one fallback query
        if not final_queries:
            fallback_query = f"{current_section.name}相关研究资料"
            if fallback_query.lower() not in executed_queries:
                final_queries.append(fallback_query)
                executed_queries.add(fallback_query.lower())
        
        logger.info(f"Final queries for section '{current_section.name}': {final_queries}")
        
        # Initialize section research tracking
        return {
            "search_query": final_queries,
            "section_research_count": 0,
            "section_is_sufficient": False,
            "section_knowledge_gap": "",
            "section_follow_up_queries": [],
            "max_section_research_loops": 2,  # Set conservative limit
            "executed_queries": list(executed_queries)  # Convert back to list for state
        }
        
    except Exception as e:
        logger.error(f"Failed to parse section queries: {e}")
        # Fallback queries with initialization
        fallback_queries = [f"{current_section.name} {current_section.description}"]
        return {
            "search_query": fallback_queries,
            "section_research_count": 0,
            "section_is_sufficient": False,
            "section_knowledge_gap": "",
            "section_follow_up_queries": [],
            "max_section_research_loops": 2  # Set conservative limit
        }


def write_section_content(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Write the content for a specific section based on gathered research."""
    configurable = Configuration.from_runnable_config(config)
    current_section = state.get("current_section")
    
    if not current_section:
        logger.warning("No current section in write_section_content, skipping")
        return {
            "current_section": None,
            "completed_sections": [],
            "section_research_count": 0,
            "section_is_sufficient": False,
        }
    
    # SAFETY: Check if this section was already completed to prevent duplicates
    completed_sections = state.get("completed_sections", [])
    completed_names = {section.name for section in completed_sections}
    
    if current_section.name in completed_names:
        logger.warning(f"Section '{current_section.name}' already completed, skipping to prevent duplicates")
        return {
            "current_section": None,  # Clear current section
            "completed_sections": [],  # Don't add duplicate
            "section_research_count": 0,
            "section_is_sufficient": False,
        }
    
    # Get research data
    web_research_result = state.get("web_research_result", [])
    rag_documents = state.get("rag_documents", [])
    sources_gathered = state.get("sources_gathered", [])
    
    # Create LLM for content generation
    llm = LLMFactory.create_llm(
        model_name=configurable.answer_model,
        temperature=0.7,
        max_retries=2,
        max_tokens=configurable.max_tokens,
    )
    
    # Prepare source information
    all_sources = []
    
    # Add RAG documents
    if rag_documents:
        for i, doc in enumerate(rag_documents):
            all_sources.append(f"=== 知识库来源 {i+1} ===\n{doc}\n")
    
    # Add web research
    if web_research_result:
        for i, result in enumerate(web_research_result):
            all_sources.append(f"=== 网络研究来源 {i+1} ===\n{result}\n")
    
    sources_text = "\n".join(all_sources) if all_sources else "无可用研究来源"
    
    # Create content generation prompt
    content_prompt = f"""你是一个专业的报告撰写专家。请基于提供的研究资料，为以下章节撰写详细内容：

章节名称：{current_section.name}
章节描述：{current_section.description}
目标字数：{current_section.word_count_target}字

研究资料：
{sources_text}

要求：
1. 内容要专业、准确、详实
2. 结构清晰，逻辑性强
3. 适当引用研究来源的关键信息
4. 符合学术写作规范
5. 字数接近目标要求

请直接输出章节内容，不需要额外的格式说明："""

    try:
        # Generate content
        result = llm.invoke([SystemMessage(content=content_prompt)])
        content = result.content if hasattr(result, 'content') else str(result)
        
        # Create completed section
        updated_section = ReportSection(
            name=current_section.name,
            description=current_section.description,
            requires_research=current_section.requires_research,
            word_count_target=current_section.word_count_target,
            content=content,
            completed=True
        )
        
    except Exception as e:
        logger.error(f"Failed to generate content for section '{current_section.name}': {e}")
        # Create fallback content
        content = f"# {current_section.name}\n\n{current_section.description}\n\n[内容生成失败，请稍后重试]"
        updated_section = ReportSection(
            name=current_section.name,
            description=current_section.description,
            requires_research=current_section.requires_research,
            word_count_target=current_section.word_count_target,
            content=content,
            completed=True
        )
    
    # Calculate word count (rough estimate)
    word_count = len(content.replace(" ", ""))  # For Chinese text
    
    logger.info(f"Generated {word_count} characters for section '{current_section.name}' - MARKED AS COMPLETED")
    
    return {
        "current_section": None,  # Clear current section after completion
        "completed_sections": [updated_section],
        # Reset section-level tracking for next section
        "section_research_count": 0,
        "section_is_sufficient": False,
        "section_knowledge_gap": "",
        "section_follow_up_queries": []
    }


def compile_final_long_report(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Compile all sections into the final long report."""
    report_plan = state["report_plan"]
    completed_sections = state["completed_sections"]
    
    if not report_plan or not completed_sections:
        return {"final_report": "报告生成失败：缺少必要信息"}
    
    # Create a mapping of completed sections
    section_content_map = {section.name: section.content for section in completed_sections}
    
    # Build the final report
    report_parts = []
    
    # Add title and abstract
    report_parts.append(f"# {report_plan.title}")
    report_parts.append(f"\n## 摘要\n\n{report_plan.abstract}\n")
    
    # Add table of contents
    report_parts.append("## 目录\n")
    for i, section in enumerate(report_plan.sections, 1):
        report_parts.append(f"{i}. {section.name}")
    report_parts.append("")
    
    # Add each section content
    for i, section in enumerate(report_plan.sections, 1):
        content = section_content_map.get(section.name, f"[{section.name}章节内容缺失]")
        report_parts.append(f"## {i}. {section.name}\n\n{content}\n")
    
    final_report = "\n".join(report_parts)
    
    # Calculate total word count
    total_words = len(final_report.replace(" ", ""))
    
    logger.info(f"Compiled final report with {total_words} characters")
    
    return {
        "final_report": final_report,
        "total_word_count": total_words
    }


def generate_complete_long_report(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """一站式长报告生成器，在单个函数中完成所有工作，避免图循环问题。"""
    configurable = Configuration.from_runnable_config(config)
    
    messages = state.get("messages", [])
    research_topic = get_research_topic(messages)
    target_word_count = state.get("target_word_count", 10000)
    
    logger.info(f"开始一站式长报告生成：{research_topic}，目标字数：{target_word_count}")
    
    try:
        # 创建LLM
        llm = LLMFactory.create_llm(
            model_name=configurable.answer_model,
            temperature=0.7,
            max_retries=2,
            max_tokens=4000,
        )
        
        # 生成简化的报告计划
        simple_sections = [
            {"name": "引言与背景", "description": "介绍研究主题的背景和重要性", "target_words": target_word_count // 5},
            {"name": "核心内容分析", "description": "深入分析主要内容和关键要点", "target_words": target_word_count // 2},
            {"name": "应用与影响", "description": "探讨实际应用和社会影响", "target_words": target_word_count // 5},
            {"name": "总结与展望", "description": "总结要点并展望未来发展", "target_words": target_word_count // 10},
        ]
        
        # 生成报告标题
        title_prompt = f"为研究主题'{research_topic}'生成一个专业的报告标题，直接输出标题，不需要其他内容："
        title_result = llm.invoke([SystemMessage(content=title_prompt)])
        title = title_result.content if hasattr(title_result, 'content') else f"{research_topic}研究报告"
        
        # 生成摘要
        abstract_prompt = f"""为主题'{research_topic}'写一个200字左右的报告摘要，简要概述研究内容和主要观点："""
        abstract_result = llm.invoke([SystemMessage(content=abstract_prompt)])
        abstract = abstract_result.content if hasattr(abstract_result, 'content') else f"本报告针对{research_topic}进行深入研究和分析。"
        
        # 构建报告内容
        report_parts = []
        report_parts.append(f"# {title}")
        report_parts.append(f"\n## 摘要\n\n{abstract}\n")
        
        # 添加目录
        report_parts.append("## 目录\n")
        for i, section in enumerate(simple_sections, 1):
            report_parts.append(f"{i}. {section['name']}")
        report_parts.append("")
        
        # 生成各章节内容
        total_generated_words = 0
        for i, section in enumerate(simple_sections, 1):
            try:
                logger.info(f"生成章节 {i}: {section['name']}")
                
                section_prompt = f"""你是专业的报告撰写专家。请为以下研究报告章节撰写详细内容：

报告主题：{research_topic}
章节名称：{section['name']}
章节描述：{section['description']}
目标字数：{section['target_words']}字

要求：
1. 内容要专业、准确、有深度
2. 结构清晰，逻辑严谨
3. 语言流畅，表达清楚
4. 可以基于常识和专业知识进行阐述
5. 使用适当的小标题组织内容

请直接输出章节内容，不需要标题编号："""

                section_result = llm.invoke([SystemMessage(content=section_prompt)])
                section_content = section_result.content if hasattr(section_result, 'content') else f"[{section['name']}章节内容生成失败]"
                
                # 添加章节到报告
                report_parts.append(f"## {i}. {section['name']}\n\n{section_content}\n")
                
                # 统计字数
                section_words = len(section_content.replace(" ", ""))
                total_generated_words += section_words
                logger.info(f"章节 {i} 完成，生成 {section_words} 字符")
                
                # 防止生成过长，如果已经接近目标就停止
                if total_generated_words >= target_word_count * 0.8:
                    logger.info(f"已生成足够内容（{total_generated_words}字符），停止生成更多章节")
                    break
                    
            except Exception as e:
                logger.error(f"生成章节 {i} 时出错: {e}")
                report_parts.append(f"## {i}. {section['name']}\n\n[该章节内容生成失败，请稍后重试]\n")
        
        # 合并最终报告
        final_report = "\n".join(report_parts)
        final_word_count = len(final_report.replace(" ", ""))
        
        logger.info(f"一站式长报告生成完成！总字数：{final_word_count}")
        
        return {
            "final_report": final_report,
            "total_word_count": final_word_count,
            "is_long_report": True,
            "report_completed": True
        }
        
    except Exception as e:
        logger.error(f"一站式长报告生成失败: {e}")
        
        # 生成fallback报告
        fallback_report = f"""# {research_topic}研究报告

## 摘要

本报告旨在对{research_topic}进行全面分析和研究。

## 1. 引言

{research_topic}是当前重要的研究领域，具有重要的理论价值和实践意义。

## 2. 核心分析

通过深入研究，我们发现{research_topic}在多个方面都有重要的发展和应用。

## 3. 总结

{research_topic}的研究和应用前景广阔，值得进一步深入探讨。

[注：由于系统限制，本报告为简化版本]"""

        return {
            "final_report": fallback_report,
            "total_word_count": len(fallback_report.replace(" ", "")),
            "is_long_report": True,
            "report_completed": True
        }


def should_generate_long_report(state: OverallState) -> str:
    """简化的长报告检测路由函数。"""
    if state.get("is_long_report", False):
        return "long_report"
    else:
        return "standard_flow"


def get_next_section(state: OverallState) -> Dict[str, Any]:
    """Get the next section that needs to be processed."""
    report_plan = state.get("report_plan")
    completed_sections = state.get("completed_sections", [])
    
    if not report_plan:
        return {"current_section": None}
    
    # SAFETY: Check for excessive processing
    section_processing_count = state.get("section_processing_count", 0)
    section_processing_count += 1
    
    # CIRCUIT BREAKER: Limit total section processing to prevent infinite loops
    max_total_sections = 10  # Hard limit on total sections to process
    if section_processing_count > max_total_sections:
        logger.warning(f"CIRCUIT BREAKER: Too many section processing attempts ({section_processing_count}), forcing termination")
        return {
            "current_section": None,
            "section_processing_count": section_processing_count
        }
    
    # Find sections that need research and haven't been completed
    completed_names = {section.name for section in completed_sections}
    
    # SAFETY: Limit to first few sections only
    sections_to_check = report_plan.sections[:5]  # Only process first 5 sections
    
    for section in sections_to_check:
        if section.requires_research and section.name not in completed_names:
            logger.info(f"Next section to process: {section.name} (attempt {section_processing_count})")
            return {
                "current_section": section,
                "section_processing_count": section_processing_count
            }
    
    # No more sections need research
    logger.info(f"No more sections to process after {section_processing_count} attempts")
    return {
        "current_section": None,
        "section_processing_count": section_processing_count
    }


def has_more_sections(state: OverallState) -> str:
    """Check if there are more sections to process."""
    # SAFETY: Check for excessive loop attempts
    section_processing_count = state.get("section_processing_count", 0)
    
    # CIRCUIT BREAKER: Force termination after reasonable number of attempts
    if section_processing_count >= 8:  # Conservative limit
        logger.warning(f"CIRCUIT BREAKER: Reached section processing limit ({section_processing_count}), forcing finalization")
        return "finalize_long_report"
    
    next_section_result = get_next_section(state)
    
    if next_section_result["current_section"] is not None:
        logger.info(f"More sections available, continuing (count: {section_processing_count})")
        return "process_section"
    else:
        logger.info(f"No more sections, finalizing report (count: {section_processing_count})")
        return "finalize_long_report" 


def section_reflection(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Reflection for a specific section to determine if more research is needed."""
    configurable = Configuration.from_runnable_config(config)
    
    current_section = state.get("current_section")
    if not current_section:
        logger.warning("No current section in section_reflection, marking as sufficient")
        return {"section_is_sufficient": True, "section_knowledge_gap": "", "section_follow_up_queries": []}
    
    # SUPER AGGRESSIVE safety check: ALWAYS mark as sufficient for now to prevent loops
    section_research_count = state.get("section_research_count", 0)
    
    # CIRCUIT BREAKER: Always mark as sufficient to prevent infinite loops
    logger.warning(f"CIRCUIT BREAKER ACTIVATED: Section '{current_section.name}' research count: {section_research_count}, FORCING sufficient to prevent loops")
    return {"section_is_sufficient": True, "section_knowledge_gap": "", "section_follow_up_queries": []}


def evaluate_section_research(state: OverallState) -> str:
    """Evaluate if section research is sufficient or needs more iterations."""
    section_is_sufficient = state.get("section_is_sufficient", True)
    section_follow_up_queries = state.get("section_follow_up_queries", [])
    current_section = state.get("current_section")
    section_research_count = state.get("section_research_count", 0)
    
    # AGGRESSIVE termination strategy to prevent infinite loops
    
    # Safety check: if no current section, ALWAYS end research
    if not current_section:
        logger.warning("No current section in evaluate_section_research, FORCING write_section_content")
        return "write_section_content"
    
    # VERY conservative limits
    max_section_research_loops = state.get("max_section_research_loops", 1)  # Even more conservative
    max_loops = min(max_section_research_loops or 1, 1)  # Maximum 1 iteration only
    
    # AGGRESSIVE termination conditions - bias towards termination
    should_terminate = (
        section_is_sufficient or                           # Research is sufficient
        not section_follow_up_queries or                   # No more queries
        section_research_count >= max_loops or             # Hit max iterations (1)
        section_research_count >= 1 or                     # Hard safety limit (1)
        len(section_follow_up_queries) == 0                # Extra check for empty queries
    )
    
    # LOG EVERYTHING for debugging
    logger.info(f"evaluate_section_research for '{current_section.name}': "
               f"sufficient={section_is_sufficient}, "
               f"queries_count={len(section_follow_up_queries)}, "
               f"research_count={section_research_count}, "
               f"max_loops={max_loops}, "
               f"should_terminate={should_terminate}")
    
    if should_terminate:
        logger.info(f"TERMINATING section research for '{current_section.name}' -> write_section_content")
        return "write_section_content"
    else:
        logger.warning(f"CONTINUING section research for '{current_section.name}' -> continue_section_research (THIS SHOULD RARELY HAPPEN)")
        return "continue_section_research"


def continue_section_research(state: OverallState) -> Dict[str, Any]:
    """Continue research for the current section with follow-up queries."""
    section_follow_up_queries = state.get("section_follow_up_queries", [])
    current_section = state.get("current_section")
    section_research_count = state.get("section_research_count", 0)
    
    # Multiple safety checks with forced termination
    if not section_follow_up_queries or not current_section:
        logger.warning("No follow-up queries or current section, forcing termination")
        return {
            "section_is_sufficient": True,
            "section_follow_up_queries": [],
            "section_research_count": section_research_count + 10  # Force high count to prevent loops
        }
    
    # Increment section research count FIRST
    section_research_count = section_research_count + 1
    
    # Hard safety limits - multiple checks
    max_section_research_loops = state.get("max_section_research_loops", 2) or 2
    
    if (section_research_count >= max_section_research_loops or 
        section_research_count >= 2 or  # Hard limit
        len(section_follow_up_queries) == 0):
        
        logger.warning(f"FORCED TERMINATION: Max research loops reached for '{current_section.name}' "
                      f"(count: {section_research_count}, max: {max_section_research_loops})")
        return {
            "section_is_sufficient": True,
            "section_follow_up_queries": [],  # Clear all follow-up queries
            "section_research_count": section_research_count + 10  # Force very high count
        }
    
    # Use the first follow-up query
    next_query = section_follow_up_queries[0]
    
    logger.info(f"Continuing section research for '{current_section.name}' with query: {next_query} (iteration {section_research_count})")
    
    return {
        "search_query": [next_query],
        "section_follow_up_queries": section_follow_up_queries[1:],  # Remove used query
        "section_research_count": section_research_count
    } 