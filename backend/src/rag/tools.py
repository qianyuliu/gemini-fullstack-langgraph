"""RAG tool integration for LangChain agents."""

import logging
from typing import List, Optional, Type, Any, Dict
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from .builder import build_retriever, is_rag_enabled
from .retriever import Retriever, Resource, Document
from .config import rag_config

logger = logging.getLogger(__name__)


class RAGSearchInput(BaseModel):
    """Input schema for RAG search tool."""
    query: str = Field(description="Search query to look up in the knowledge base")
    max_results: Optional[int] = Field(
        default=None, 
        description="Maximum number of documents to return"
    )


class RAGSearchTool(BaseTool):
    """RAG search tool for retrieving information from knowledge base."""
    
    name: str = "rag_search"
    description: str = (
        "Search for information in the knowledge base using RAG (Retrieval-Augmented Generation). "
        "This tool should be used when you need to find specific information from uploaded documents "
        "or configured knowledge sources. Input should be a clear search query."
    )
    args_schema: Type[BaseModel] = RAGSearchInput
    
    retriever: Optional[Retriever] = Field(default=None)
    resources: List[Resource] = Field(default_factory=list)
    
    def __init__(self, resources: Optional[List[Resource]] = None, **kwargs):
        super().__init__(**kwargs)
        self.resources = resources or []
        self.retriever = build_retriever()
        
        if not self.retriever:
            logger.warning("RAG retriever not available, tool will return empty results")
    
    def _run(
        self,
        query: str,
        max_results: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute RAG search synchronously."""
        if not self.retriever:
            return "RAG is not configured or not available. Please check your configuration."
        
        try:
            logger.info(f"RAG search query: {query}")
            logger.debug(f"Available resources: {len(self.resources)}")
            
            # Use configured max_results or global config
            max_docs = max_results or rag_config.max_documents
            
            documents = self.retriever.query_relevant_documents(query, self.resources)
            
            if not documents:
                return "No relevant information found in the knowledge base."
            
            # Limit results
            documents = documents[:max_docs]
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(documents, 1):
                doc_text = f"## Document {i}: {doc.title}\n\n"
                
                # Log chunk similarities for debugging
                if doc.chunks:
                    similarities = [chunk.similarity for chunk in doc.chunks]
                    logger.info(f"Document {i} chunk similarities: {similarities}")
                    logger.info(f"Similarity threshold: {rag_config.similarity_threshold}")
                
                # Filter chunks by similarity threshold
                relevant_chunks = [
                    chunk for chunk in doc.chunks 
                    if chunk.similarity >= rag_config.similarity_threshold
                ]
                
                if not relevant_chunks:
                    # If no chunks meet threshold, take the best chunks anyway
                    logger.warning(f"No chunks meet similarity threshold {rag_config.similarity_threshold}, using all chunks")
                    relevant_chunks = doc.chunks[:3]  # Take top 3 chunks
                
                for chunk in relevant_chunks:
                    doc_text += f"**Content:** {chunk.content}\n"
                    doc_text += f"**Similarity:** {chunk.similarity:.3f}\n\n"
                
                formatted_results.append(doc_text)
            
            result = "\n".join(formatted_results)
            logger.info(f"RAG search returned {len(documents)} documents")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during RAG search: {e}")
            return f"Error occurred during knowledge base search: {str(e)}"
    
    async def _arun(
        self,
        query: str,
        max_results: Optional[int] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Execute RAG search asynchronously."""
        # For now, just call the synchronous version
        return self._run(query, max_results, run_manager.get_sync() if run_manager else None)


def create_rag_tool(resources: Optional[List[Resource]] = None) -> Optional[RAGSearchTool]:
    """Create a RAG search tool if RAG is enabled and configured.
    
    Args:
        resources: List of resources to search within
        
    Returns:
        RAG search tool instance or None if not available
    """
    if not is_rag_enabled():
        logger.info("RAG is not enabled, skipping RAG tool creation")
        return None
        
    try:
        logger.info("Creating RAG search tool")
        return RAGSearchTool(resources=resources)
    except Exception as e:
        logger.error(f"Failed to create RAG tool: {e}")
        return None


def get_rag_tool_info() -> Dict[str, Any]:
    """Get information about RAG tool availability and configuration."""
    return {
        "enabled": is_rag_enabled(),
        "provider": rag_config.provider,
        "max_documents": rag_config.max_documents,
        "similarity_threshold": rag_config.similarity_threshold,
    } 