#!/usr/bin/env python3
"""
Test script to verify tool integration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fetcher import smart_fetch, fetch_with_xreach, fetch_with_jina
from search_provider import search_topic, search_with_ask_search, search_with_ddgs


def test_search():
    """Test search integration"""
    print("=" * 60)
    print("Testing Search Integration")
    print("=" * 60)
    
    query = "OpenClaw AI agent"
    
    # Test ask-search
    print("\n1. Testing ask-search...")
    results = search_with_ask_search(query, limit=3)
    if results:
        print(f"   ✅ ask-search available: {len(results)} results")
        for r in results[:2]:
            print(f"      - {r['title'][:50]}...")
    else:
        print("   ⚠️  ask-search not available (will use fallback)")
    
    # Test DuckDuckGo fallback
    print("\n2. Testing DuckDuckGo fallback...")
    results = search_with_ddgs(query, limit=3)
    if results:
        print(f"   ✅ DuckDuckGo available: {len(results)} results")
        for r in results[:2]:
            print(f"      - {r['title'][:50]}...")
    else:
        print("   ❌ DuckDuckGo not available")
    
    # Test unified search_topic
    print("\n3. Testing unified search_topic...")
    results = search_topic(query, limit=3)
    if results:
        print(f"   ✅ search_topic works: {len(results)} results")
    else:
        print("   ❌ search_topic failed")


def test_fetch():
    """Test fetch integration"""
    print("\n" + "=" * 60)
    print("Testing Fetch Integration")
    print("=" * 60)
    
    test_url = "https://example.com"
    
    # Test xreach (for Twitter/X)
    print("\n1. Testing xreach (Twitter/X tool)...")
    result = fetch_with_xreach(test_url)
    if result.success:
        print(f"   ✅ xreach available")
        print(f"      Content length: {len(result.content)} chars")
    else:
        print(f"   ⚠️  xreach: {result.failure_label}")
        print(f"      Reason: {result.error_message}")
    
    # Test Jina Reader
    print("\n2. Testing Jina Reader...")
    result = fetch_with_jina(test_url)
    if result.success:
        print(f"   ✅ Jina Reader works")
        print(f"      Content length: {len(result.content)} chars")
    else:
        print(f"   ❌ Jina Reader failed: {result.error_message}")
    
    # Test smart_fetch
    print("\n3. Testing smart_fetch...")
    result = smart_fetch(test_url, strategy="auto")
    if result.success:
        print(f"   ✅ smart_fetch works")
        print(f"      Tool used: {result.tool_used}")
        print(f"      Content length: {len(result.content)} chars")
    else:
        print(f"   ❌ smart_fetch failed: {result.failure_label}")


def main():
    print("\n" + "=" * 60)
    print("OpenClaw Layered Search - Integration Test")
    print("=" * 60)
    
    test_search()
    test_fetch()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("""
The system will work with whatever tools are available:
- ✅ = Tool is working
- ⚠️  = Tool not available, will use fallback
- ❌ = Critical failure

Even if some tools show ⚠️, the system will still function
with reduced capabilities.

To enable optional tools:
- ask-search: https://github.com/ythx-101/ask-search
- Agent-Reach: pip install https://github.com/Panniantong/agent-reach/archive/main.zip
    """)


if __name__ == "__main__":
    main()
