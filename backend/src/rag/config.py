"""RAG provider configuration module."""

import os
import enum
from typing import Optional
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
# Try to find .env file in current directory or parent directories
env_file = find_dotenv()
if env_file:
    load_dotenv(env_file)
    print(f"DEBUG: Loaded environment from {env_file}")
else:
    load_dotenv()
    print("DEBUG: No .env file found, using system environment variables")


class RAGProvider(enum.Enum):
    """Supported RAG providers."""
    RAGFLOW = "ragflow"
    VIKINGDB = "vikingdb"  # 预留扩展
    LOCAL_VECTOR = "local_vector"  # 预留扩展


class RAGConfig:
    """RAG configuration management."""
    
    def __init__(self):
        self.provider = os.getenv("RAG_PROVIDER", "").lower()
        self.enabled = bool(self.provider)
        
        # RAGFlow specific configurations
        self.ragflow_api_url = os.getenv("RAGFLOW_API_URL")
        self.ragflow_api_key = os.getenv("RAGFLOW_API_KEY") 
        self.ragflow_page_size = int(os.getenv("RAGFLOW_RETRIEVAL_SIZE", "10"))
        
        # Common configurations
        self.max_documents = int(os.getenv("RAG_MAX_DOCUMENTS", "5"))
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.1"))
        self.enable_fallback = os.getenv("RAG_ENABLE_FALLBACK", "true").lower() == "true"
        
    def validate(self) -> bool:
        """Validate current configuration."""
        if not self.enabled:
            return True
            
        if self.provider == RAGProvider.RAGFLOW.value:
            return bool(self.ragflow_api_url and self.ragflow_api_key)
            
        return False
    
    def get_provider_type(self) -> Optional[RAGProvider]:
        """Get the configured provider type."""
        try:
            return RAGProvider(self.provider)
        except ValueError:
            return None


# Global configuration instance
rag_config = RAGConfig() 