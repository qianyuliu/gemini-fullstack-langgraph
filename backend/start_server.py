#!/usr/bin/env python3
"""Start the LangGraph server with proper configuration for RAGFlow."""

import subprocess
import sys
import os

def start_server():
    """Start the LangGraph development server with blocking calls allowed."""
    
    print("🚀 Starting LangGraph server with RAGFlow support...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    print(f"Working directory: {backend_dir}")
    
    # Command to start the server
    cmd = [
        "langgraph", "dev", 
        "--host", "0.0.0.0", 
        "--port", "2024",
        "--allow-blocking"  # Allow blocking calls for RAGFlow
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ LangGraph CLI not found. Please install it:")
        print("pip install langgraph-cli")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 