# Installation Guide

## Quick Start

### 1. Install core dependencies

```bash
cd openclaw-layered-search
pip install -r requirements.txt
```

This installs:
- `playwright` - for browser automation
- `beautifulsoup4` - for HTML parsing
- `duckduckgo-search` - for search (fallback)

### 2. Install Playwright browsers

```bash
playwright install chromium
```

## Optional: Enhanced Capabilities

For full functionality, install these optional tools:

### ask-search (Recommended for better search)

**What it does:** Aggregates search results from Google, Bing, DuckDuckGo, Brave via self-hosted SearxNG.

**Installation:**
```bash
# Clone the repository
git clone https://github.com/ythx-101/ask-search.git
cd ask-search

# Follow installation instructions in their README
# Typically involves:
# 1. Setting up SearxNG (Docker recommended)
# 2. Installing the ask-search CLI
```

**Verification:**
```bash
ask-search "test query" --num 5
```

If this works, OpenClaw Layered Search will automatically use it for topic searches.

### Agent-Reach (Recommended for platform scraping)

**What it does:** Provides platform-specific scraping for Twitter/X, 小红书, YouTube, GitHub, etc.

**Installation:**
```bash
# Clone the repository
git clone https://github.com/Panniantong/Agent-Reach.git ~/.openclaw/workspace/Agent-Reach
cd ~/.openclaw/workspace/Agent-Reach

# Install dependencies
pip install -e .

# Follow platform-specific setup in their docs
# For example, to enable Twitter scraping:
# - Export cookies using Cookie-Editor Chrome extension
# - Configure Agent-Reach with the cookies
```

**Verification:**
```bash
cd ~/.openclaw/workspace/Agent-Reach
python3 -c "from agent_reach.core import AgentReach; print('Agent-Reach available')"
```

If this works, OpenClaw Layered Search will automatically use it for URL fetching.

## Verification

Test your installation:

```bash
cd openclaw-layered-search/src

# Test basic URL fetch
python3 pipeline.py "https://example.com"

# Test topic search
python3 cli.py "OpenClaw features"

# Test mixed mode
python3 cli.py "AI agents https://example.com"
```

## Troubleshooting

### ask-search not found

If you see "ask-search not found" in logs:
- OpenClaw Layered Search will fall back to DuckDuckGo search
- This is fine for basic usage
- For better results, install ask-search following the steps above

### Agent-Reach not available

If you see "Agent-Reach not installed" in logs:
- OpenClaw Layered Search will fall back to basic HTTP + Jina Reader
- This works for most URLs
- For platform-specific content (Twitter, 小红书), install Agent-Reach

### Import errors

If you see Python import errors:
```bash
# Make sure you're in the right directory
cd openclaw-layered-search

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Architecture

```
OpenClaw Layered Search
    ├─ Core (always available)
    │   ├─ Basic HTTP fetching
    │   ├─ Jina Reader fallback
    │   └─ DuckDuckGo search
    │
    └─ Enhanced (optional)
        ├─ ask-search → better search results
        └─ Agent-Reach → platform-specific scraping
```

The system works without optional tools, but with reduced capabilities.

## Next Steps

After installation:
1. Read [README.md](README.md) for usage examples
2. Read [SKILL.md](skill/SKILL.md) for OpenClaw integration
3. Try the demos in the README
4. Configure optional tools for enhanced capabilities
