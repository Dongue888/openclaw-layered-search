"""
Search provider module: integrates multiple search engines
- ask-search (SearxNG aggregator) - preferred
- DuckDuckGo - fallback
"""

from __future__ import annotations

import json
import subprocess
from typing import List, Dict, Optional


def search_with_ask_search(query: str, limit: int = 10) -> Optional[List[Dict[str, str]]]:
    """
    Search using ask-search (SearxNG aggregator)
    
    ask-search aggregates results from Google, Bing, DuckDuckGo, Brave
    Zero API key required, self-hosted
    
    Returns None if ask-search is not available
    """
    try:
        result = subprocess.run(
            ["ask-search", query, "--num", str(limit), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return None
        
        data = json.loads(result.stdout)
        results = []
        
        # Parse ask-search JSON format
        for item in data.get("results", []):
            url = item.get("link") or item.get("url") or ""
            title = item.get("title") or ""
            snippet = item.get("snippet") or item.get("content") or ""
            
            if url:
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": snippet
                })
        
        return results if results else None
        
    except FileNotFoundError:
        # ask-search not installed
        return None
    except subprocess.TimeoutExpired:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def search_with_ddgs(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search using DuckDuckGo (fallback)
    
    Used when ask-search is not available
    """
    try:
        # Try new package name first
        try:
            from ddgs import DDGS
        except ImportError:
            # Fall back to old package name
            from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=limit):
                url = item.get("href") or item.get("url") or ""
                title = item.get("title") or ""
                body = item.get("body") or item.get("snippet") or ""
                
                if url:
                    results.append({
                        "url": url,
                        "title": title,
                        "snippet": body
                    })
        
        return results
        
    except ImportError:
        # Neither package installed
        return []
    except Exception:
        return []


def search_topic(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search for topic using best available search engine
    
    Priority:
    1. ask-search (SearxNG aggregator) - preferred
    2. DuckDuckGo - fallback
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        List of search results with url, title, snippet
    """
    # Try ask-search first
    results = search_with_ask_search(query, limit)
    
    if results:
        return results
    
    # Fallback to DuckDuckGo
    results = search_with_ddgs(query, limit)
    
    return results
