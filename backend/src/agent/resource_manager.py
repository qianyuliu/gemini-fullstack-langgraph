"""Resource management for RAG system."""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import os

from src.rag import Resource, is_rag_enabled, rag_config

logger = logging.getLogger(__name__)


@dataclass
class ResourceConfig:
    """Configuration for a RAG resource."""
    name: str
    uri: str
    title: str
    description: str = ""
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ResourceManager:
    """Manager for RAG resources."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("RAG_RESOURCES_CONFIG", "resources.json")
        self.resources: Dict[str, ResourceConfig] = {}
        self.load_resources()
    
    def load_resources(self) -> None:
        """Load resources from configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for resource_data in data.get('resources', []):
                        resource_config = ResourceConfig(**resource_data)
                        self.resources[resource_config.name] = resource_config
                logger.info(f"Loaded {len(self.resources)} resources from {self.config_path}")
            else:
                logger.info(f"No resource configuration file found at {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load resources: {e}")
    
    def save_resources(self) -> None:
        """Save resources to configuration file."""
        try:
            data = {
                'resources': [
                    {
                        'name': resource.name,
                        'uri': resource.uri,
                        'title': resource.title,
                        'description': resource.description,
                        'enabled': resource.enabled,
                        'metadata': resource.metadata
                    }
                    for resource in self.resources.values()
                ]
            }
            
            # Ensure directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.resources)} resources to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save resources: {e}")
    
    def add_resource(self, name: str, uri: str, title: str, description: str = "", 
                    enabled: bool = True, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a new resource."""
        resource_config = ResourceConfig(
            name=name,
            uri=uri,
            title=title,
            description=description,
            enabled=enabled,
            metadata=metadata or {}
        )
        self.resources[name] = resource_config
        logger.info(f"Added resource: {name}")
    
    def remove_resource(self, name: str) -> bool:
        """Remove a resource."""
        if name in self.resources:
            del self.resources[name]
            logger.info(f"Removed resource: {name}")
            return True
        return False
    
    def get_resource(self, name: str) -> Optional[ResourceConfig]:
        """Get a resource by name."""
        return self.resources.get(name)
    
    def list_resources(self, enabled_only: bool = True) -> List[ResourceConfig]:
        """List all resources."""
        if enabled_only:
            return [r for r in self.resources.values() if r.enabled]
        return list(self.resources.values())
    
    def get_rag_resources(self, resource_names: Optional[List[str]] = None) -> List[Resource]:
        """Get Resource objects for RAG system."""
        if resource_names:
            # Get specific resources
            configs = [self.resources.get(name) for name in resource_names]
            configs = [c for c in configs if c and c.enabled]
        else:
            # Get all enabled resources
            configs = self.list_resources(enabled_only=True)
        
        resources = []
        for config in configs:
            resource = Resource(
                uri=config.uri,
                title=config.title,
                description=config.description
            )
            resources.append(resource)
        
        return resources
    
    def validate_resources(self) -> Dict[str, List[str]]:
        """Validate all resources and return any issues."""
        issues = {}
        
        for name, resource in self.resources.items():
            resource_issues = []
            
            # Check URI format
            if not resource.uri:
                resource_issues.append("URI is empty")
            elif not resource.uri.startswith("rag://"):
                resource_issues.append("URI should start with 'rag://'")
            
            # Check title
            if not resource.title:
                resource_issues.append("Title is empty")
            
            if resource_issues:
                issues[name] = resource_issues
        
        return issues
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get statistics about managed resources."""
        enabled_count = len(self.list_resources(enabled_only=True))
        total_count = len(self.resources)
        
        return {
            "total_resources": total_count,
            "enabled_resources": enabled_count,
            "disabled_resources": total_count - enabled_count,
            "rag_enabled": is_rag_enabled(),
            "rag_provider": rag_config.provider if rag_config.enabled else None,
        }


# Global resource manager instance
resource_manager = ResourceManager()


def get_default_resources() -> List[Resource]:
    """Get default resources from resource manager."""
    return resource_manager.get_rag_resources()


def get_resources_by_names(names: List[str]) -> List[Resource]:
    """Get specific resources by names."""
    return resource_manager.get_rag_resources(names) 