from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, List, Optional, Dict, Any, Literal
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage

from langgraph.graph import add_messages
from typing_extensions import TypedDict
import operator

try:
    from src.rag import Resource
except ImportError:
    try:
        # Fallback for relative imports
        from ..rag import Resource
    except ImportError:
        # Create a simple Resource class if import fails
        class Resource:
            def __init__(self, uri: str, title: str, description: str):
                self.uri = uri
                self.title = title
                self.description = description
from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    """Report section model for long report generation."""
    name: str = Field(description="Name of the report section")
    description: str = Field(description="Brief description of what this section should cover")
    requires_research: bool = Field(description="Whether this section needs research")
    content: str = Field(default="", description="Generated content for this section")
    word_count_target: int = Field(default=1000, description="Target word count for this section")
    research_queries: List[str] = Field(default_factory=list, description="Specific research queries for this section")
    completed: bool = Field(default=False, description="Whether this section is completed")
    # New fields for enhanced processing
    research_iterations: int = Field(default=0, description="Number of research iterations performed")
    rag_content: List[str] = Field(default_factory=list, description="RAG retrieved content for this section")
    web_content: List[str] = Field(default_factory=list, description="Web search content for this section")
    reflection_result: Optional[str] = Field(default=None, description="Reflection result for this section")
    sources_used: List[Dict[str, str]] = Field(default_factory=list, description="Sources used in this section")


class ReportPlan(BaseModel):
    """Complete report plan with sections."""
    title: str = Field(description="Title of the report")
    abstract: str = Field(description="Brief abstract of the report")
    sections: List[ReportSection] = Field(description="List of report sections")
    total_word_count_target: int = Field(description="Target word count for entire report")


class SectionGenerationResult(BaseModel):
    """Result of section generation."""
    section_name: str
    content: str
    sources_used: List[Dict[str, str]]
    word_count: int
    quality_score: float


# New state classes for chapter-by-chapter processing
class SectionState(TypedDict):
    """State for individual section processing."""
    # Section-specific state
    section: ReportSection
    
    # Research state
    search_queries: List[str]
    research_iterations: int
    max_research_iterations: int
    
    # Content state
    rag_content: List[str]
    web_content: List[str]
    combined_content: List[str]
    
    # Reflection state
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: List[str]
    reflection_result: str
    
    # Core message state
    messages: List[BaseMessage]
    
    # RAG and web search configuration
    rag_resources: List[str]
    rag_enabled: bool
    
    # Final output
    completed_section: Optional[ReportSection]


class SectionOutputState(TypedDict):
    """Output state for section processing."""
    completed_section: ReportSection
    sources_used: List[Dict[str, str]]
    total_research_iterations: int


# Existing state classes
class OverallState(TypedDict):
    """Overall state for the research agent."""
    
    # Core conversation state
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Research query and planning
    search_query: List[str]
    initial_search_query_count: Optional[int]
    
    # RAG-related state
    rag_resources: List[str]  # List of RAG resource URIs
    rag_documents: List[str]  # Retrieved RAG documents
    rag_enabled: bool  # Whether RAG is enabled for this session
    
    # Search and research state
    sources_gathered: Annotated[List[Dict[str, Any]], operator.add]
    web_research_result: Annotated[List[str], operator.add]
    
    # Reflection and iteration state
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: List[str]
    research_loop_count: int
    number_of_ran_queries: int
    max_research_loops: Optional[int]
    
    # Model selection
    reasoning_model: Optional[str]
    
    # Long report specific fields
    is_long_report: bool
    target_word_count: Optional[int]  # Target word count for long reports
    report_plan: Optional[ReportPlan]
    current_section: Optional[ReportSection]
    completed_sections: List[ReportSection]  # Remove operator.add to prevent accumulation
    final_report: Optional[str]
    
    # Section-level reflection fields
    section_is_sufficient: bool
    section_knowledge_gap: str
    section_follow_up_queries: List[str]
    section_research_count: int
    max_section_research_loops: Optional[int]
    
    # Query deduplication
    executed_queries: List[str]  # Track executed queries to avoid duplicates
    
    # New fields for chapter-by-chapter processing
    section_processing_results: Annotated[List[SectionOutputState], operator.add]
    current_section_index: int
    total_sections: int
    sections_completed_count: int  # Track number of completed sections for frontend display
    next_section_index: Optional[int]  # Track next section to process for routing
    
    # Configuration for section processing
    max_section_research_iterations: Optional[int]


class ReflectionState(TypedDict):
    """State for reflection phase."""
    messages: List[BaseMessage]
    web_research_result: Optional[List[str]]
    rag_documents: Optional[List[str]]
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: List[str]
    research_loop_count: int
    number_of_ran_queries: int
    max_research_loops: Optional[int]


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    """State for query generation phase."""
    messages: List[BaseMessage]
    search_query: List[str]
    initial_search_query_count: Optional[int]


class WebSearchState(TypedDict):
    """State for web search phase."""
    messages: List[BaseMessage]
    search_query: List[str]
    sources_gathered: List[Dict[str, Any]]
    web_research_result: List[str]


class RAGState(TypedDict):
    """State for RAG retrieval phase."""
    messages: List[BaseMessage]
    rag_resources: Optional[List[str]]
    rag_documents: Optional[List[str]]
    rag_enabled: Optional[bool]


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: Optional[str] = field(default=None)  # Final report


def create_rag_resources(uris: List[str]) -> List[Resource]:
    """Create Resource objects from URIs.
    
    Args:
        uris: List of resource URIs
        
    Returns:
        List of Resource objects
    """
    resources = []
    for uri in uris:
        resource = Resource(
            uri=uri,
            title=f"Resource {uri}",
            description=""
        )
        resources.append(resource)
    return resources


def get_combined_research_content(state: OverallState) -> List[str]:
    """Get combined research content from both RAG and web search.
    
    Args:
        state: Current state
        
    Returns:
        Combined list of research content
    """
    content = []
    
    # Add RAG documents if available
    rag_documents = state.get("rag_documents")
    if rag_documents:
        content.extend(rag_documents)
    
    # Add web research results
    web_research_result = state.get("web_research_result")
    if web_research_result:
        content.extend(web_research_result)
    
    return content
