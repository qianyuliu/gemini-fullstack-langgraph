"""Builder function for RAG retrieval providers."""

import logging
from typing import Optional

from .config import rag_config, RAGProvider
from .retriever import Retriever
from .ragflow import RAGFlowProvider

logger = logging.getLogger(__name__)


def build_retriever() -> Optional[Retriever]:
    """Build and return a retriever instance based on environment configuration.
    
    Returns:
        A retriever instance if configured, None otherwise
    """
    if not rag_config.enabled:
        logger.info("RAG is not enabled, no provider configured")
        return None
        
    if not rag_config.validate():
        logger.error("RAG configuration validation failed")
        return None
    
    provider_type = rag_config.get_provider_type()
    
    if provider_type == RAGProvider.RAGFLOW:
        try:
            logger.info("Initializing RAGFlow provider")
            return RAGFlowProvider()
        except Exception as e:
            logger.error(f"Failed to initialize RAGFlow provider: {e}")
            if rag_config.enable_fallback:
                logger.warning("RAG fallback is enabled, but no fallback provider configured")
            return None
    
    elif provider_type == RAGProvider.VIKINGDB:
        logger.error("VikingDB provider is not implemented yet")
        return None
        
    elif provider_type == RAGProvider.LOCAL_VECTOR:
        logger.error("Local vector provider is not implemented yet")
        return None
        
    else:
        logger.error(f"Unsupported RAG provider: {rag_config.provider}")
        return None


def get_available_providers() -> list[str]:
    """Get list of available RAG providers."""
    return [provider.value for provider in RAGProvider]


def is_rag_enabled() -> bool:
    """Check if RAG is enabled and properly configured."""
    return rag_config.enabled and rag_config.validate() 