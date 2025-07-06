from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict, List, Optional, Dict, Any
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage

from langgraph.graph import add_messages
from typing_extensions import TypedDict
import operator

from src.rag import Resource


class OverallState(TypedDict):
    """Overall state for the research agent."""
    
    # Core conversation state
    messages: List[BaseMessage]
    
    # Research query and planning
    search_query: Optional[str | List[str]]
    initial_search_query_count: Optional[int]
    
    # RAG-related state
    rag_resources: Optional[List[str]]  # List of RAG resource URIs
    rag_documents: Optional[List[str]]  # Retrieved RAG documents
    rag_enabled: Optional[bool]  # Whether RAG is enabled for this session
    
    # Search and research state
    sources_gathered: Optional[List[Dict[str, Any]]]
    web_research_result: Optional[List[str]]
    
    # Reflection and iteration state
    is_sufficient: Optional[bool]
    knowledge_gap: Optional[str]
    follow_up_queries: Optional[List[str]]
    research_loop_count: Optional[int]
    number_of_ran_queries: Optional[int]
    max_research_loops: Optional[int]
    
    # Model selection
    reasoning_model: Optional[str]


class ReflectionState(TypedDict):
    """State for reflection phase."""
    messages: List[BaseMessage]
    web_research_result: Optional[List[str]]
    rag_documents: Optional[List[str]]
    is_sufficient: Optional[bool]
    knowledge_gap: Optional[str]
    follow_up_queries: Optional[List[str]]
    research_loop_count: Optional[int]
    number_of_ran_queries: Optional[int]
    max_research_loops: Optional[int]


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    """State for query generation phase."""
    messages: List[BaseMessage]
    search_query: Optional[str | List[str]]
    initial_search_query_count: Optional[int]


class WebSearchState(TypedDict):
    """State for web search phase."""
    messages: List[BaseMessage]
    search_query: Optional[str | List[str]]
    sources_gathered: Optional[List[Dict[str, Any]]]
    web_research_result: Optional[List[str]]


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
