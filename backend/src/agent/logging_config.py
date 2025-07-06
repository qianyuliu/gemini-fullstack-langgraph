"""Logging configuration for the enhanced RAG system."""

import logging
import os
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to logs/rag_system.log)
        log_format: Custom log format string
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
    """
    # Get log level from environment or use provided value
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    
    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Default log file
    if log_file is None:
        log_file = os.getenv("LOG_FILE", "logs/rag_system.log")
    
    # Ensure log directory exists
    if enable_file and log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler
    if enable_file and log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
    
    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(f"Logging configured - Level: {log_level}, Console: {enable_console}, File: {enable_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class RAGSystemLogger:
    """Enhanced logger for RAG system operations."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_rag_operation(self, operation: str, details: Optional[dict] = None, level: str = "INFO"):
        """Log RAG-specific operations with structured data."""
        details = details or {}
        message = f"RAG Operation: {operation}"
        
        if details:
            detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" - {detail_str}"
        
        getattr(self.logger, level.lower())(message)
    
    def log_retrieval(self, query: str, num_results: int, provider: Optional[str] = None):
        """Log retrieval operations."""
        details = {
            "query": query[:100] + "..." if len(query) > 100 else query,
            "num_results": num_results,
            "provider": provider or "unknown"
        }
        self.log_rag_operation("RETRIEVAL", details)
    
    def log_error(self, operation: str, error: Exception, context: Optional[dict] = None):
        """Log errors with context information."""
        context = context or {}
        message = f"RAG Error in {operation}: {str(error)}"
        
        if context:
            context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
            message += f" - Context: {context_str}"
        
        self.logger.error(message, exc_info=True)
    
    def log_performance(self, operation: str, duration: float, details: Optional[dict] = None):
        """Log performance metrics."""
        details = details or {}
        details["duration_ms"] = round(duration * 1000, 2)
        self.log_rag_operation(f"PERFORMANCE_{operation}", details)
    
    def log_config_change(self, config_name: str, old_value: str, new_value: str):
        """Log configuration changes."""
        details = {
            "config": config_name,
            "old_value": old_value,
            "new_value": new_value
        }
        self.log_rag_operation("CONFIG_CHANGE", details, "INFO")


# Initialize default logging
def init_default_logging():
    """Initialize default logging configuration."""
    setup_logging(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        enable_console=os.getenv("LOG_CONSOLE", "true").lower() == "true",
        enable_file=os.getenv("LOG_FILE_ENABLED", "true").lower() == "true",
    )


# Auto-initialize if not already done
if not logging.getLogger().handlers:
    init_default_logging() 