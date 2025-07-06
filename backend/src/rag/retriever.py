"""Base classes and interfaces for RAG retrieval system."""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class Resource(BaseModel):
    """Represents a RAG resource (e.g., a dataset or document)."""
    uri: str
    title: str
    description: str = ""


class Chunk(BaseModel):
    """Represents a chunk of text from a document."""
    content: str
    similarity: float = 0.0


class Document(BaseModel):
    """Represents a document with its chunks."""
    id: str
    title: str
    chunks: List[Chunk] = []


class Retriever(ABC):
    """Abstract base class for RAG retrieval providers."""
    
    @abstractmethod
    def query_relevant_documents(
        self, query: str, resources: List[Resource] = []
    ) -> List[Document]:
        """Query relevant documents based on the query and optional resources.
        
        Args:
            query: The search query
            resources: Optional list of resources to search within
            
        Returns:
            List of relevant documents with their chunks
        """
        pass
    
    @abstractmethod
    def list_resources(self, query: Optional[str] = None) -> List[Resource]:
        """List available resources from the RAG provider.
        
        Args:
            query: Optional query to filter resources
            
        Returns:
            List of available resources
        """
        pass 