"""Web search tool for performing web searches using various search engines."""

import os
import json
import requests
from typing import List, Dict, Any
from urllib.parse import quote_plus


class WebSearchTool:
    """A flexible web search tool that supports multiple search engines."""
    
    def __init__(self):
        self.search_engine = os.getenv("SEARCH_ENGINE", "duckduckgo")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a web search using the configured search engine.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and url
        """
        if self.search_engine == "tavily" and self.tavily_api_key:
            return self._search_tavily(query, max_results)
        elif self.search_engine == "serper" and self.serper_api_key:
            return self._search_serper(query, max_results)
        elif self.search_engine == "google" and self.google_api_key and self.google_cse_id:
            return self._search_google(query, max_results)
        else:
            return self._search_duckduckgo(query, max_results)
    
    def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Tavily API."""
        try:
            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}
            data = {
                "api_key": self.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            return [
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("content", ""),
                    "url": result.get("url", ""),
                    "source": "tavily"
                }
                for result in results
            ]
        except Exception as e:
            print(f"Tavily search failed: {e}")
            return []
    
    def _search_serper(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Serper API."""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            data = {
                "q": query,
                "num": max_results
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            results = response.json().get("organic", [])
            return [
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "source": "serper"
                }
                for result in results
            ]
        except Exception as e:
            print(f"Serper search failed: {e}")
            return []
    
    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": query,
                "num": min(max_results, 10)
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            results = response.json().get("items", [])
            return [
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "source": "google"
                }
                for result in results
            ]
        except Exception as e:
            print(f"Google search failed: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (simple fallback)."""
        try:
            # This is a basic implementation - in production you might want to use
            # a proper DuckDuckGo search library or API
            url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            # For demo purposes, return a simple response
            # In real implementation, you'd parse the HTML response
            return [
                {
                    "title": f"Search results for: {query}",
                    "snippet": "DuckDuckGo search result (fallback mode)",
                    "url": url,
                    "source": "duckduckgo"
                }
            ]
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            return []
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into a readable string."""
        if not results:
            return "No search results found."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"""
{i}. {result.get('title', 'No title')}
   {result.get('snippet', 'No snippet available')}
   URL: {result.get('url', 'No URL')}
"""
            formatted_results.append(formatted_result)
        
        return "\n".join(formatted_results)


# Global instance
web_search_tool = WebSearchTool() 