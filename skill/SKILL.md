---
name: openclaw-layered-search
description: Intelligent retrieval orchestration for OpenClaw. Auto-detects input type (URL/Topic/Mixed), plans retrieval strategy, handles failures with fallback, and tracks evidence. Reduces hallucinations by grounding answers in retrieved content.
---

# OpenClaw Layered Search

**Intelligent retrieval orchestration for OpenClaw agents.**

## What it does

Helps your agent choose the right retrieval strategy before answering:

- **Input understanding**: Auto-detects URL, Topic, or Mixed mode
- **Strategy planning**: Decides which tool to use and in what order
- **Failure handling**: Classifies failures and tries intelligent fallbacks
- **Evidence tracking**: Records what worked, what failed, and why

## Why use this?

### Problem
When you give an agent a URL or ask it to search for information:
- It doesn't know which tool to use (web_fetch? agent-reach? search?)
- When fetching fails, it guesses or hallucinates
- It can't combine multiple sources intelligently
- You don't know what actually happened during retrieval

### Solution
This skill orchestrates retrieval tools to:
- ✅ Choose the right tool automatically
- ✅ Fallback sanely when things fail
- ✅ Track evidence and explain uncertainties
- ✅ Ground summaries in retrieved content only

## Usage

### Single URL
```bash
python3 src/pipeline.py "https://example.com/article"
```

Returns structured JSON with:
- `retrieval_path`: which tools were tried
- `sources_retrieved`: successful fetches
- `sources_failed`: failures with labels
- `summary`: grounded in retrieved content
- `uncertainties`: what's missing or unclear

### Topic search
```bash
python3 src/cli.py "OpenClaw features"
```

Automatically:
1. Searches for candidate sources
2. Ranks candidates by relevance
3. Fetches top sources
4. Returns structured summary with source list

### Mixed mode (topic + references)
```bash
python3 src/cli.py "AI agents https://example.com/article"
```

Intelligently:
1. Detects mixed input
2. Prioritizes user-provided URLs first
3. Expands search only if needed
4. Combines multiple sources

## Output format

```json
{
  "input_type": "url|topic|mixed",
  "retrieval_path": ["web_fetch", "r.jina.ai"],
  "sources_retrieved": [
    {
      "url": "...",
      "title": "...",
      "content": "..."
    }
  ],
  "sources_failed": [
    {
      "url": "...",
      "failure_label": "blocked_placeholder",
      "attempted_tools": ["web_fetch"]
    }
  ],
  "summary": "...",
  "uncertainties": ["..."],
  "next_actions": ["..."]
}
```

## Failure labels

The skill classifies failures to help agents understand what went wrong:

- `blocked_placeholder`: JavaScript-rendered page (empty content)
- `weak_content`: Content too short or low quality
- `login_wall`: Requires authentication
- `network_error`: Connection failed
- `not_implemented`: Feature not yet supported
- `unknown`: Unclassified failure

## Integration with other tools

This skill orchestrates existing tools:

- **ask-search**: For topic search (via SearxNG)
- **Agent-Reach**: For platform-specific scraping (Twitter, 小红书, etc)
- **r.jina.ai**: For JavaScript-heavy pages
- **web_fetch**: For basic HTTP requests

You don't need to know which tool to use — the skill decides for you.

## Installation

```bash
cd ~/.openclaw/workspace
git clone <your-repo-url> openclaw-layered-search
cd openclaw-layered-search
pip install -r requirements.txt
```

### Optional dependencies

For full functionality, install:

1. **ask-search** (for topic search)
   ```bash
   # See: https://github.com/ythx-101/ask-search
   ```

2. **Agent-Reach** (for platform scraping)
   ```bash
   # See: https://github.com/Panniantong/Agent-Reach
   ```

The skill will work without these, but with reduced capabilities.

## Examples

### Example 1: Article URL
```bash
python3 src/pipeline.py "https://www.stcn.com/article/detail/3666565.html"
```

Output:
- Tries `web_fetch` first
- Extracts title and content
- Returns grounded summary

### Example 2: Twitter/X post
```bash
python3 src/pipeline.py "https://x.com/user/status/123"
```

Output:
- Detects JavaScript placeholder
- Falls back to `r.jina.ai`
- Extracts post content
- Records failure path

### Example 3: Research query
```bash
python3 src/cli.py "How does OpenClaw handle tool selection?"
```

Output:
- Searches for candidates
- Ranks by relevance
- Fetches top 3-5 sources
- Returns structured summary with source list

## Configuration

Currently uses default settings. Future versions will support:
- Custom tool priorities
- Fallback strategies
- Timeout settings
- Parallel fetch limits

## Limitations

Current MVP limitations:
- Browser fallback not yet implemented
- Topic search needs ask-search installed
- Platform scraping needs Agent-Reach installed
- No caching yet (fetches every time)

## Roadmap

- [ ] Full integration with ask-search and Agent-Reach
- [ ] Browser fallback for hard pages
- [ ] Parallel fetching optimization
- [ ] Caching layer
- [ ] OpenClaw-native tool integration
- [ ] Custom configuration support

## Contributing

This is an open-source project. Contributions welcome!

Areas that need help:
- Better failure classification
- More fallback strategies
- Performance optimization
- Documentation improvements

## License

MIT

---

**Key insight:** The hard problem isn't "can I scrape this URL?" — it's "how should I answer this question?"

This skill solves the orchestration problem, not the scraping problem.
