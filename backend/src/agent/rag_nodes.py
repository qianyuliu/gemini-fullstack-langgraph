"""RAG integration nodes for the LangGraph agent."""

import logging
from typing import List, Optional, Dict, Any
from langchain_core.runnables import RunnableConfig

from rag import create_rag_tool, Resource, is_rag_enabled, rag_config
# Import state and utils locally to avoid circular imports
# from src.agent.state import OverallState, create_rag_resources
# from src.agent.utils import get_research_topic

logger = logging.getLogger(__name__)


def rag_retrieve(state, config: RunnableConfig) -> Dict[str, Any]:
    """LangGraph node that retrieves documents from RAG sources.
    
    Enhanced version that uses the new RAG tool architecture with better error handling.
    
    Args:
        state: Current graph state containing the research topic and RAG resources
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update, including rag_documents with retrieved content
    """
    # Import locally to avoid circular imports
    from state import create_rag_resources
    from utils import get_research_topic
    
    logger.info("Starting RAG retrieval")
    
    # Check if RAG is enabled
    if not is_rag_enabled():
        logger.info("RAG is not enabled, skipping retrieval")
        return {"rag_documents": [], "rag_enabled": False}
    
    # Get the research topic from messages
    # Convert BaseMessage to AnyMessage for compatibility
    messages = state["messages"]
    research_topic = get_research_topic(messages)
    if not research_topic:
        logger.warning("No research topic found in messages")
        return {"rag_documents": [], "rag_enabled": True}
    
    # Convert URIs to Resource objects
    resources = []
    resource_uris = state.get("rag_resources", [])
    if resource_uris:
        resources = create_rag_resources(resource_uris)
        logger.info(f"Using {len(resources)} RAG resources")
    else:
        logger.info("No specific RAG resources provided, using default search")
    
    # Create RAG tool
    rag_tool = create_rag_tool(resources)
    if not rag_tool:
        logger.error("Failed to create RAG tool")
        return {"rag_documents": [], "rag_enabled": True}
    
    try:
        # Perform RAG retrieval using the tool
        logger.info(f"Performing RAG search for: {research_topic}")
        result = rag_tool.invoke({
            "query": research_topic,
            "max_results": rag_config.max_documents
        })
        
        if isinstance(result, str):
            if "No relevant information found" in result or "not configured" in result:
                logger.warning(f"RAG search returned no results: {result}")
                return {"rag_documents": [], "rag_enabled": True}
            else:
                logger.info("RAG search completed successfully")
                return {"rag_documents": [result], "rag_enabled": True}
        else:
            logger.warning(f"Unexpected RAG tool result type: {type(result)}")
            return {"rag_documents": [], "rag_enabled": True}
            
    except Exception as e:
        logger.error(f"Error during RAG retrieval: {e}")
        return {"rag_documents": [], "rag_enabled": True}


def has_rag_resources(state) -> bool:
    """Check if the state has RAG resources configured."""
    return bool(state.get("rag_resources", []))


def should_use_rag(state) -> str:
    """Enhanced routing function to determine if RAG should be used.
    
    Args:
        state: Current state
        
    Returns:
        "rag_retrieve" if RAG should be used, "web_research" otherwise
    """
    # Check if RAG is enabled globally
    if not is_rag_enabled():
        logger.info("RAG is not enabled, routing to web research")
        return "web_research"
    
    # Check if user has specified RAG resources
    if has_rag_resources(state):
        logger.info("RAG resources found, routing to RAG retrieval")
        return "rag_retrieve"
    
    # Check if RAG is configured for general use
    if rag_config.enabled:
        logger.info("RAG is enabled for general use, routing to RAG retrieval")
        return "rag_retrieve"
    
    logger.info("No RAG configuration found, routing to web research")
    return "web_research"


def rag_fallback_to_web(state) -> str:
    """Routing function to determine if we should fallback to web search after RAG.
    
    Args:
        state: Current state
        
    Returns:
        "web_research" if fallback is needed, "reflection" otherwise
    """
    rag_documents = state.get("rag_documents", [])
    
    # If no RAG documents were retrieved and fallback is enabled
    if not rag_documents and rag_config.enable_fallback:
        logger.info("No RAG documents found, falling back to web research")
        return "web_research"
    
    # If we have RAG documents, proceed to reflection
    if rag_documents:
        logger.info("RAG documents found, proceeding to reflection")
        return "reflection"
    
    # If fallback is disabled, still proceed to reflection
    logger.info("RAG fallback is disabled, proceeding to reflection")
    return "reflection" 