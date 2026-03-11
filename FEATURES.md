# Feature Matrix

## What Works Out of the Box?

After `pip install -r requirements.txt`, you get:

| Feature | Status | Notes |
|---------|--------|-------|
| **Basic URL Fetching** | ✅ Works | HTTP/HTTPS pages |
| **JavaScript Pages** | ✅ Works | Via Jina Reader fallback |
| **Web Search** | ✅ Works | Via DuckDuckGo |
| **Failure Tracking** | ✅ Works | Full failure classification |
| **Smart Fallback** | ✅ Works | Automatic strategy selection |
| **Mixed Mode** | ✅ Works | Topic + references |

**Good for:**
- News sites, blogs, documentation
- Basic research tasks
- Most everyday use cases

**Limitations:**
- Twitter/X: May get placeholder content
- 小红书: May be blocked
- Search quality: Basic (single engine)

## What Needs Optional Tools?

### With ask-search

Install: https://github.com/ythx-101/ask-search

| Feature | Improvement |
|---------|-------------|
| **Search Quality** | ⬆️ Much better (aggregates 4 engines) |
| **Search Results** | ⬆️ More diverse sources |
| **Search Speed** | ⬆️ Faster (self-hosted) |

**Installation effort:** Medium (requires SearxNG setup)

### With Agent-Reach

Install: https://github.com/Panniantong/Agent-Reach

| Platform | Without | With Agent-Reach |
|----------|---------|------------------|
| **Twitter/X** | ⚠️ Placeholder content | ✅ Full tweets |
| **小红书** | ❌ Blocked | ✅ Full content |
| **YouTube** | ⚠️ No subtitles | ✅ Subtitles + metadata |
| **B站** | ❌ Blocked | ✅ Full content |
| **GitHub** | ✅ Basic | ✅ Advanced features |

**Installation effort:** Medium (requires platform configuration)

## Quick Decision Guide

### "I just want to try it"
→ Use basic installation
→ Works for 80% of use cases

### "I need Twitter/X support"
→ Install Agent-Reach
→ Configure Twitter cookies

### "I need best search quality"
→ Install ask-search
→ Set up SearxNG

### "I want everything"
→ Install both
→ Full feature unlock

## Installation Comparison

### Minimal (5 minutes)
```bash
git clone <repo>
pip install -r requirements.txt
```
**You get:** Core functionality, works immediately

### Enhanced (30 minutes)
```bash
# Minimal install +
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
```
**You get:** + Platform-specific scraping

### Complete (1 hour)
```bash
# Enhanced install +
git clone https://github.com/ythx-101/ask-search
# Follow ask-search setup (Docker + SearxNG)
```
**You get:** + Best search quality

## Recommendation

**For most users:** Start with minimal installation
- Try it out
- See if it meets your needs
- Install optional tools only if needed

**For power users:** Go straight to complete installation
- Unlock all features immediately
- Best experience for complex tasks

## Feature Roadmap

Future plans to reduce dependencies:

- [ ] Built-in Twitter/X support (without Agent-Reach)
- [ ] Built-in search aggregation (without ask-search)
- [ ] One-command setup for optional tools
- [ ] Docker image with everything pre-installed

## FAQ

**Q: Can I use this without any optional tools?**
A: Yes! Core functionality works out of the box.

**Q: Which optional tool should I install first?**
A: Depends on your use case:
- Need Twitter/X? → Agent-Reach
- Need better search? → ask-search

**Q: Is it hard to install optional tools?**
A: Medium difficulty. Both require some setup, but have good documentation.

**Q: Can I install optional tools later?**
A: Yes! The system auto-detects them when available.

**Q: Do optional tools cost money?**
A: No, both are free and open-source. You may need a proxy ($1/month) for some platforms.
