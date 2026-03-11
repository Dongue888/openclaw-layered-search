# OpenClaw Layered Search Demo Notes

## Demo command

### Article page
```bash
cd openclaw-layered-search
python3 src/cli.py "https://www.stcn.com/article/detail/3666565.html"
```

### X post
```bash
cd openclaw-layered-search
python3 src/cli.py "https://x.com/jain_web3/status/2029428696646598883"
```

### Topic mode
```bash
cd openclaw-layered-search
python3 src/cli.py "OpenClaw Layered Search"
```

### Mixed mode
```bash
cd openclaw-layered-search
python3 src/cli.py "OpenClaw Layered Search https://www.stcn.com/article/detail/3666565.html https://x.com/jain_web3/status/2029428696646598883"
```

## What to point out in a demo

### For article links
- it does not need search first
- it tries direct retrieval first
- it extracts article-like body instead of raw page noise
- it gives a grounded summary

### For X links
- it detects the JavaScript placeholder page
- it labels the initial failure as `blocked_placeholder`
- it falls back to `r.jina.ai`
- it extracts the post body instead of returning the whole page shell

### For topic mode
- it starts with search instead of pretending it already knows the answer
- it shows candidate sources before summarizing
- it makes the selected sources visible
- it produces a structured topic summary instead of a blind merge

### For mixed mode
- it detects that the user already provided seed references
- it prioritizes those references before expanding outward
- it keeps the research grounded in the user-provided evidence
- it treats broader search as an optional next step, not the first reflex

## Core pitch

This project is not trying to be “another scraper”.

It is trying to make OpenClaw agents more reliable at external information access:
- better tool ordering
- better fallback behavior
- fewer hallucinations after failed retrieval
