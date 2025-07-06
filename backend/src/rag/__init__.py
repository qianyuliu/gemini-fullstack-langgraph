"""RAG (Retrieval-Augmented Generation) module for document retrieval and management."""

from .retriever import Retriever, Resource, Document, Chunk
from .ragflow import RAGFlowProvider
from .builder import build_retriever, get_available_providers, is_rag_enabled
from .config import rag_config, RAGProvider, RAGConfig
from .tools import RAGSearchTool, create_rag_tool, get_rag_tool_info

__all__ = [
    # Base classes
    "Retriever",
    "Resource", 
    "Document",
    "Chunk",
    
    # Providers
    "RAGFlowProvider",
    
    # Builder functions
    "build_retriever",
    "get_available_providers",
    "is_rag_enabled",
    
    # Configuration
    "rag_config",
    "RAGProvider",
    "RAGConfig",
    
    # Tools
    "RAGSearchTool",
    "create_rag_tool",
    "get_rag_tool_info",
] 