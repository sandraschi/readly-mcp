# readly-mcp v0.2.0 — Intelligence Upgrade SPEC

**Date**: 2026-04-29
**Goal**: Transform readly-mcp from a basic screenshot scraper into a content-intelligence
source that aiwatcher-mcp can ingest as a feed.

---

## Current State (v0.1.0)

4 MCP tools: `open_readly_browser`, `smart_scrape` (screenshot + PDF), `get_status`, `stop_scrape`.
No text extraction, no article listing, no search. aiwatcher-mcp cannot use it.

## Target State (v0.2.0)

3 new MCP tools for content intelligence + REST endpoints + aiwatcher-mcp integration.

---

## Tool 1: `list_articles`

**What**: Parse the currently open Readly magazine/issue page to extract article headlines.

**How**: Use Playwright's `page.evaluate()` to run JavaScript in the browser context
that traverses the DOM looking for article cards. Readly's article structure uses
elements with classes containing "track", "article", "issue-page", etc.

**Returns**:
```json
{
  "issue_title": "Wired UK — May 2026",
  "articles": [
    {"title": "The AI Takeover of Brussels", "url": "https://go.readly.com/...", "index": 0},
    {"title": "Why Quantum Computing Will Never Work", "url": "https://go.readly.com/...", "index": 1}
  ],
  "count": 12
}
```

**Fallback**: If DOM parsing fails, return the current page title and URL so the user
can manually navigate.

---

## Tool 2: `extract_article_text`

**What**: Given an article index (from `list_articles`), click the article, wait for it to
load, and extract the full text content.

**How**: Click the article card, wait for the reader view, then extract text from the
article content container.

**Returns**:
```json
{
  "title": "The AI Takeover of Brussels",
  "url": "https://go.readly.com/...",
  "author": "Jane Doe",
  "text": "Full article text...",
  "word_count": 842
}
```

---

## Tool 3: `search_magazines`

**What**: Navigate to Readly's search/catalog and search for magazines by keyword.

**How**: Navigate to `https://go.readly.com/search?q={query}` and parse results.

**Returns**:
```json
{
  "query": "ai",
  "results": [
    {"title": "Wired UK", "url": "https://go.readly.com/...", "type": "magazine"},
    {"title": "MIT Technology Review", "url": "...", "type": "magazine"}
  ],
  "count": 5
}
```

---

## aiwatcher-mcp Integration Module

New file: `aiwatcher_mcp/readly_ingestion.py`

- Calls `list_articles` on readly-mcp REST API every 6h (configurable)
- Extracts articles that match enabled bundles
- Inserts as items with feed_type="readly"
- Benefits from existing distillation pipeline (Claude scoring, alerts, digest)

---

## REST Endpoints (FastAPI)

- `POST /api/articles/list` — calls `list_articles`
- `POST /api/articles/extract?index=N` — calls `extract_article_text`
- `GET /api/magazines/search?q=QUERY` — calls `search_magazines`
