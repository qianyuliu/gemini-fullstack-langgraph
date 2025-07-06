"""
Enhanced RAG System Example

This example demonstrates how to use the improved RAG system with:
- Multiple RAG providers support
- Resource management
- Enhanced logging
- Better error handling
- Performance monitoring
"""

import os
import asyncio
from typing import List, Dict, Any

# Set up environment variables
os.environ["RAG_PROVIDER"] = "ragflow"
os.environ["RAGFLOW_API_URL"] = "http://localhost:9380"
os.environ["RAGFLOW_API_KEY"] = "your-api-key-here"
os.environ["RAG_MAX_DOCUMENTS"] = "3"
os.environ["RAG_SIMILARITY_THRESHOLD"] = "0.7"
os.environ["LOG_LEVEL"] = "INFO"

from src.rag import (
    rag_config,
    create_rag_tool,
    Resource,
    is_rag_enabled,
    get_rag_tool_info
)
from src.agent.resource_manager import resource_manager
from src.agent.logging_config import RAGSystemLogger

# Initialize logger
logger = RAGSystemLogger(__name__)


def setup_example_resources():
    """Setup example RAG resources."""
    logger.log_rag_operation("SETUP_RESOURCES", {"action": "start"})
    
    # Add some example resources
    resource_manager.add_resource(
        name="knowledge_base_1",
        uri="rag://dataset/kb1",
        title="General Knowledge Base",
        description="Contains general information about various topics",
        metadata={"priority": "high", "last_updated": "2024-01-15"}
    )
    
    resource_manager.add_resource(
        name="technical_docs",
        uri="rag://dataset/tech_docs",
        title="Technical Documentation", 
        description="Technical documentation and API references",
        metadata={"priority": "medium", "domain": "technical"}
    )
    
    resource_manager.add_resource(
        name="research_papers",
        uri="rag://dataset/papers",
        title="Research Papers",
        description="Academic research papers and publications",
        enabled=False,  # Disabled for this example
        metadata={"priority": "low", "domain": "academic"}
    )
    
    # Save resources to file
    resource_manager.save_resources()
    
    logger.log_rag_operation("SETUP_RESOURCES", {
        "action": "complete",
        "total_resources": len(resource_manager.resources),
        "enabled_resources": len(resource_manager.list_resources(enabled_only=True))
    })


def demonstrate_rag_configuration():
    """Demonstrate RAG configuration and validation."""
    print("=== RAG Configuration ===")
    print(f"RAG Enabled: {is_rag_enabled()}")
    print(f"Provider: {rag_config.provider}")
    print(f"Max Documents: {rag_config.max_documents}")
    print(f"Similarity Threshold: {rag_config.similarity_threshold}")
    print(f"Fallback Enabled: {rag_config.enable_fallback}")
    print(f"Configuration Valid: {rag_config.validate()}")
    print()
    
    # Get RAG tool info
    tool_info = get_rag_tool_info()
    print("Tool Info:", tool_info)
    print()


def demonstrate_resource_management():
    """Demonstrate resource management capabilities."""
    print("=== Resource Management ===")
    
    # List all resources
    all_resources = resource_manager.list_resources(enabled_only=False)
    print(f"Total Resources: {len(all_resources)}")
    
    for resource in all_resources:
        print(f"  - {resource.name}: {resource.title} ({'enabled' if resource.enabled else 'disabled'})")
    print()
    
    # Get enabled resources for RAG
    rag_resources = resource_manager.get_rag_resources()
    print(f"Enabled RAG Resources: {len(rag_resources)}")
    for resource in rag_resources:
        print(f"  - {resource.title}: {resource.uri}")
    print()
    
    # Validate resources
    issues = resource_manager.validate_resources()
    if issues:
        print("Resource Issues:")
        for name, resource_issues in issues.items():
            print(f"  - {name}: {', '.join(resource_issues)}")
    else:
        print("All resources are valid")
    print()
    
    # Get statistics
    stats = resource_manager.get_resource_stats()
    print("Resource Statistics:", stats)
    print()


def demonstrate_rag_search():
    """Demonstrate RAG search functionality."""
    print("=== RAG Search Example ===")
    
    if not is_rag_enabled():
        print("RAG is not enabled. Please configure RAG provider.")
        return
    
    # Get specific resources
    specific_resources = resource_manager.get_rag_resources(["knowledge_base_1", "technical_docs"])
    
    # Create RAG tool
    rag_tool = create_rag_tool(specific_resources)
    
    if not rag_tool:
        print("Failed to create RAG tool")
        return
    
    # Example queries
    queries = [
        "What is artificial intelligence?",
        "How to implement REST API authentication?",
        "Best practices for database design"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        try:
            # Log the search
            logger.log_retrieval(query, rag_config.max_documents, rag_config.provider)
            
            # Perform search
            result = rag_tool.invoke({
                "query": query,
                "max_results": 2
            })
            
            # Display result
            if isinstance(result, str):
                print(result[:500] + "..." if len(result) > 500 else result)
            else:
                print(f"Unexpected result type: {type(result)}")
                
        except Exception as e:
            logger.log_error("RAG_SEARCH", e, {"query": query})
            print(f"Error during search: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("=== Error Handling Example ===")
    
    # Simulate various error conditions
    test_cases = [
        {
            "name": "Invalid Provider",
            "setup": lambda: setattr(rag_config, 'provider', 'invalid_provider'),
            "cleanup": lambda: setattr(rag_config, 'provider', 'ragflow')
        },
        {
            "name": "Empty Query",
            "query": ""
        },
        {
            "name": "Very Long Query", 
            "query": "A" * 10000
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        try:
            if 'setup' in test_case:
                test_case['setup']()
            
            if 'query' in test_case:
                # Try to create tool and search
                rag_tool = create_rag_tool()
                if rag_tool:
                    result = rag_tool.invoke({"query": test_case['query']})
                    print(f"Result: {result[:100]}...")
                else:
                    print("Failed to create RAG tool")
            
        except Exception as e:
            logger.log_error(test_case['name'], e)
            print(f"Error (expected): {e}")
        
        finally:
            if 'cleanup' in test_case:
                test_case['cleanup']()


def main():
    """Main function to run all examples."""
    print("Enhanced RAG System Example")
    print("=" * 50)
    
    # Setup
    setup_example_resources()
    
    # Demonstrate different aspects
    demonstrate_rag_configuration()
    demonstrate_resource_management()
    demonstrate_rag_search()
    demonstrate_error_handling()
    
    print("\nExample completed!")


if __name__ == "__main__":
    main() 