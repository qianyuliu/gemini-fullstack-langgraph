"""RAGFlow integration for RAG retrieval."""

import os
import requests
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from .retriever import Retriever, Resource, Document, Chunk


class RAGFlowProvider(Retriever):
    """RAGFlow provider for document retrieval and resource management."""
    
    def __init__(self):
        """Initialize RAGFlow provider with API credentials."""
        print(f"DEBUG: Initializing RAGFlowProvider")
        # Remove os.getcwd() call to avoid blocking in ASGI environment
        
        self.api_url = os.getenv("RAGFLOW_API_URL")
        print(f"DEBUG: RAGFLOW_API_URL from env: {self.api_url}")
        
        if not self.api_url:
            raise ValueError("RAGFLOW_API_URL environment variable is not set")
        
        # Handle common URL configuration issues
        if self.api_url == "http://localhost":
            self.api_url = "http://localhost:9380"
            print("Warning: RAGFLOW_API_URL was missing port, using default :9380")
        
        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')
        print(f"DEBUG: Final API URL: {self.api_url}")
        
        self.api_key = os.getenv("RAGFLOW_API_KEY")
        if not self.api_key:
            raise ValueError("RAGFLOW_API_KEY environment variable is not set")
        
        print(f"DEBUG: RAGFLOW_API_KEY: {'Set' if self.api_key else 'Not set'}")
        
        self.page_size = int(os.getenv("RAGFLOW_RETRIEVAL_SIZE", "10"))
    
    def query_relevant_documents(
        self, query: str, resources: List[Resource] = []
    ) -> List[Document]:
        """Query relevant documents from RAGFlow."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        dataset_ids = []
        document_ids = []
        
        # Parse resources to extract dataset and document IDs
        for resource in resources:
            dataset_id, document_id = self._parse_uri(resource.uri)
            dataset_ids.append(dataset_id)
            if document_id:
                document_ids.append(document_id)
        
        payload = {
            "question": query,
            "dataset_ids": dataset_ids,
            "document_ids": document_ids,
            "page_size": self.page_size,
        }
        
        print(f"DEBUG: RAG tool API call")
        print(f"DEBUG: URL: {self.api_url}/api/v1/retrieval")
        print(f"DEBUG: Headers: {headers}")
        print(f"DEBUG: Payload: {payload}")
        
        response = requests.post(
            f"{self.api_url}/api/v1/retrieval",
            headers=headers,
            json=payload
        )
        
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response text: {response.text[:500]}...")
        
        if response.status_code != 200:
            raise Exception(f"Failed to query documents: {response.text}")
        
        result = response.json()
        data = result.get("data", {})
        
        print(f"DEBUG: RAGFlow response data keys: {list(data.keys())}")
        print(f"DEBUG: Number of doc_aggs: {len(data.get('doc_aggs', []))}")
        print(f"DEBUG: Number of chunks: {len(data.get('chunks', []))}")
        
        # Create documents from aggregated results
        docs = {}
        for doc_agg in data.get("doc_aggs", []):
            doc_id = doc_agg.get("doc_id")
            doc_name = doc_agg.get("doc_name", "")
            print(f"DEBUG: Creating document {doc_id}: {doc_name}")
            docs[doc_id] = Document(
                id=doc_id,
                title=doc_name,
                chunks=[]
            )
        
        # Add chunks to documents
        for i, chunk in enumerate(data.get("chunks", [])):
            doc_id = chunk.get("document_id")
            content = chunk.get("content", "")
            similarity = chunk.get("similarity", 0.0)
            print(f"DEBUG: Chunk {i}: doc_id={doc_id}, similarity={similarity}, content_length={len(content)}")
            
            if doc_id in docs:
                docs[doc_id].chunks.append(
                    Chunk(
                        content=content,
                        similarity=similarity
                    )
                )
            else:
                print(f"DEBUG: Warning - chunk {i} references unknown document {doc_id}")
        
        print(f"DEBUG: Final documents: {len(docs)}")
        for doc_id, doc in docs.items():
            print(f"DEBUG: Document {doc_id}: {doc.title} with {len(doc.chunks)} chunks")
        
        return list(docs.values())
    
    def list_resources(self, query: Optional[str] = None) -> List[Resource]:
        """List available datasets from RAGFlow."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        params = {}
        if query:
            params["name"] = query
        
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/datasets",
                headers=headers,
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list resources: {response.text}")
            
            result = response.json()
            resources = []
            
            for item in result.get("data", []):
                resource = Resource(
                    uri=f"rag://dataset/{item.get('id')}",
                    title=item.get("name", ""),
                    description=item.get("description") or ""
                )
                resources.append(resource)
            
            return resources
        
        except requests.exceptions.ConnectionError:
            print(f"RAGFlow connection failed: Cannot connect to {self.api_url}")
            print("Please check:")
            print("1. RAGFlow server is running")
            print("2. RAGFLOW_API_URL is correct (usually http://localhost:9380)")
            print("3. No firewall blocking the connection")
            print("Returning test data for development.")
            return [
                Resource(
                    uri="rag://dataset/test-1",
                    title="测试知识库1",
                    description="这是一个测试知识库，包含技术文档"
                ),
                Resource(
                    uri="rag://dataset/test-2", 
                    title="测试知识库2",
                    description="这是另一个测试知识库，包含FAQ文档"
                )
            ]
        except Exception as e:
            print(f"RAGFlow error: {e}")
            print("Returning test data for development.")
            return [
                Resource(
                    uri="rag://dataset/test-1",
                    title="测试知识库1",
                    description="这是一个测试知识库，包含技术文档"
                ),
                Resource(
                    uri="rag://dataset/test-2", 
                    title="测试知识库2",
                    description="这是另一个测试知识库，包含FAQ文档"
                )
            ]
    
    def _parse_uri(self, uri: str) -> Tuple[str, str]:
        """Parse a RAG URI to extract dataset and document IDs."""
        print(f"DEBUG: Parsing URI: {uri}")
        parsed = urlparse(uri)
        print(f"DEBUG: Parsed URI - scheme: {parsed.scheme}, netloc: {parsed.netloc}, path: {parsed.path}, fragment: {parsed.fragment}")
        
        if parsed.scheme != "rag":
            raise ValueError(f"Invalid URI scheme: {uri}")
        
        # For URI like rag://dataset/ID, netloc is "dataset" and path is "/ID"
        if parsed.netloc == "dataset":
            # Extract dataset ID from path
            dataset_id = parsed.path.strip("/")
        else:
            # Fallback: try to extract from path parts
            path_parts = parsed.path.strip("/").split("/")
            print(f"DEBUG: Path parts: {path_parts}")
            if len(path_parts) >= 2 and path_parts[0] == "dataset":
                dataset_id = path_parts[1]
            else:
                dataset_id = ""
        
        # Extract document ID from fragment
        document_id = parsed.fragment if parsed.fragment else ""
        
        print(f"DEBUG: Extracted dataset_id: '{dataset_id}', document_id: '{document_id}'")
        return dataset_id, document_id 