"""Tools and schemas for the LangGraph agent."""

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from src.rag import create_rag_tool, Resource, is_rag_enabled


class SearchQueryList(BaseModel):
    """Schema for multiple search queries."""
    queries: List[str] = Field(description="List of search queries to execute")


class Reflection(BaseModel):
    """Schema for reflection on research completeness."""
    is_sufficient: bool = Field(description="Whether the research is sufficient")
    knowledge_gap: str = Field(description="Description of knowledge gaps if any")
    follow_up_queries: List[str] = Field(description="Follow-up queries to address gaps")


def get_available_tools(rag_resources: Optional[List[Resource]] = None) -> List[BaseTool]:
    """Get all available tools for the agent.
    
    Args:
        rag_resources: Optional list of RAG resources to search within
        
    Returns:
        List of available tools
    """
    tools = []
    
    # Add RAG tool if enabled
    if is_rag_enabled():
        rag_tool = create_rag_tool(rag_resources)
        if rag_tool:
            tools.append(rag_tool)
    
    # Add other tools as needed
    # tools.extend([web_search_tool, other_tools...])
    
    return tools


def create_resource_from_uri(uri: str, title: str = "", description: str = "") -> Resource:
    """Create a Resource object from URI.
    
    Args:
        uri: The resource URI
        title: Optional title for the resource
        description: Optional description for the resource
        
    Returns:
        Resource object
    """
    return Resource(
        uri=uri,
        title=title or f"Resource {uri}",
        description=description
    )
