# Use absolute imports for LangGraph compatibility
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph import research_graph as graph

__all__ = ["graph"]
