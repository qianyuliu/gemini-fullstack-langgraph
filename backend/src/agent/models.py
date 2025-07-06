"""Data models for API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel

from rag.retriever import Resource


class RAGConfigResponse(BaseModel):
    """Response model for RAG configuration."""
    provider: Optional[str] = None


class RAGResourceRequest(BaseModel):
    """Request model for RAG resources."""
    query: Optional[str] = None


class RAGResourcesResponse(BaseModel):
    """Response model for RAG resources."""
    resources: List[Resource] = []


class ConfigResponse(BaseModel):
    """Response model for general configuration."""
    rag: RAGConfigResponse 