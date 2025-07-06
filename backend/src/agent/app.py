# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import os
from typing import Annotated
from fastapi import FastAPI, Response, Query
from fastapi.staticfiles import StaticFiles

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

from rag.builder import build_retriever

# Use absolute imports for LangGraph compatibility
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import RAGConfigResponse, RAGResourceRequest, RAGResourcesResponse, ConfigResponse
from llm_factory import get_available_models

# Define the FastAPI app
app = FastAPI()


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# RAG API endpoints
@app.get("/api/rag/config", response_model=RAGConfigResponse)
async def rag_config():
    """Get the RAG configuration."""
    rag_provider = os.getenv("RAG_PROVIDER")
    return RAGConfigResponse(provider=rag_provider)


@app.get("/api/rag/resources", response_model=RAGResourcesResponse)
async def rag_resources(request: Annotated[RAGResourceRequest, Query()]):
    """Get available RAG resources."""
    print(f"DEBUG: RAG resources API called with query: {request.query}")
    print(f"DEBUG: Environment variables:")
    print(f"  RAG_PROVIDER: {os.getenv('RAG_PROVIDER')}")
    print(f"  RAGFLOW_API_URL: {os.getenv('RAGFLOW_API_URL')}")
    print(f"  RAGFLOW_API_KEY: {'Set' if os.getenv('RAGFLOW_API_KEY') else 'Not set'}")
    
    retriever = build_retriever()
    print(f"DEBUG: Retriever created: {retriever}")
    
    if retriever:
        try:
            resources = retriever.list_resources(request.query)
            print(f"DEBUG: Retrieved {len(resources)} resources")
            for resource in resources:
                print(f"  - {resource.title}: {resource.uri}")
            return RAGResourcesResponse(resources=resources)
        except Exception as e:
            print(f"DEBUG: Error retrieving resources: {e}")
            return RAGResourcesResponse(resources=[])
    
    print("DEBUG: No retriever available")
    return RAGResourcesResponse(resources=[])


@app.get("/api/config", response_model=ConfigResponse)
async def config():
    """Get the application configuration."""
    rag_provider = os.getenv("RAG_PROVIDER")
    return ConfigResponse(
        rag=RAGConfigResponse(provider=rag_provider)
    )


@app.get("/api/models")
async def get_models():
    """Get available models based on configured API keys."""
    try:
        models = get_available_models()
        return {"models": models}
    except Exception as e:
        print(f"Failed to get models: {str(e)}")
        # Return default models if none are configured
        return {"models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "provider": "deepseek"},
            {"id": "glm-4", "name": "GLM-4", "provider": "zhipuai"},
            {"id": "qwen-turbo", "name": "Qwen Turbo", "provider": "qwen"},
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
        ]}


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
