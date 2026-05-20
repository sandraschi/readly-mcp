# Product Requirements Document (PRD): Readly MCP Server

## 1. Overview
The **Readly MCP Server** is a specialized Model Context Protocol (MCP) server designed to bridge the gap between Large Language Models (LLMs) and the Readly digital magazine platform (`go.readly.com`). It allows AI agents to read, scrape, extract content from, and archive magazine issues by simulating human interaction within a browser environment.

## 2. Goals & Objectives
- **Automated Access**: Enable LLMs to access magazine content that doesn't have a public API.
- **Content Intelligence (v0.2)**: Extract structured article data (titles, URLs, full text) for downstream processing.
- **Search & Discovery (v0.2)**: Search Readly's catalog to find magazines matching topics of interest.
- **Fleet Integration (v0.2)**: Serve as a content source for `aiwatcher-mcp` via REST API.
- **Human Simulation**: Mimic human reading behavior (page turning intervals) to avoid bot detection and rate limiting.
- **Archival**: Convert transient web content into persistent PDF documents for offline reading.
- **Integration**: Provide a standard MCP interface for seamless integration with tools like Claude Desktop, Cursor, and other MCP clients.

## 3. Core Features

### 3.1 Browser Management
- **Persistent Context**: Store user session data (cookies, local storage) to maintain login state across server restarts.
- **Headless & Headed Modes**: Support both headless operation for background tasks and headed mode for initial manual login/debugging.

### 3.2 Content Intelligence (v0.2)
- **Article Listing**: DOM-based extraction of article titles, URLs from the current magazine issue page.
- **Full Text Extraction**: Navigate to individual articles and extract text content, word count, and author info.
- **Magazine Search**: Navigate to Readly's catalog and search for magazines by keyword query.

### 3.3 Scraping Engine
- **Page Navigation**: Automate "next page" actions using keyboard or mouse simulation.
- **Screenshot Capture**: High-resolution viewport capture of each page.
- **Anti-Detection**: Configurable delays and human-like interactions.

### 3.4 Output Generation
- **PDF Compilation**: Stitch captured screenshots into a single, specialized PDF file.
- **Structured Data**: JSON responses with article metadata and full text for fleet integration.

## 4. Architecture
- **Framework**: FastMCP 3.2+
- **Transport**: Stdio (primary), HTTP Streamable, SSE (capability) via `transport.py`
- **Engine**: Playwright (Async API) with persistent browser context
- **API Bridge**: FastAPI + uvicorn on configurable port (default 10863)
- **Image Processing**: Pillow & FPDF2

## 5. MCP Tools (v0.2.0)

| Tool | Type | Description |
|------|------|-------------|
| `open_readly_browser` | Browser | Open browser, navigate to readly.com |
| `list_articles` | Content | Parse DOM for article titles + URLs |
| `extract_article_text` | Content | Click article, extract full text |
| `search_magazines` | Content | Search catalog by keyword |
| `smart_scrape` | Scraping | Page-by-page screenshot → PDF |
| `get_status` | Status | Scraping job progress |
| `stop_scrape` | Control | Graceful stop |

## 6. REST API (v0.2.0)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | Scraping status |
| `/api/tools` | GET | Registered MCP tools |
| `/api/articles/list` | GET | Article listing |
| `/api/articles/extract?index=N` | GET | Article text extraction |
| `/api/magazines/search?q=QUERY` | GET | Magazine search |
| `/api/scrape/start` | POST | Start scrape job |
| `/api/scrape/stop` | POST | Stop scrape job |

## 7. Fleet Integration

readly-mcp v0.2+ integrates with `aiwatcher-mcp` as an ingestion source:
- aiwatcher-mcp calls `GET /api/articles/list` to discover articles
- Calls `GET /api/articles/extract?index=N` for full text
- Articles flow into the distillation pipeline (Claude scoring, alerts, digest)

## 8. Constraints & Assumptions
- **User Account**: A valid, paid Readly account is required.
- **Local Execution**: The server runs locally on the user's machine to leverage their IP and credentials.
- **Rate Limits**: Implicitly limited by the "human speed" constraints to prevent account banning.
- **Headful Mode Required for Login**: `open_readly_browser` must run in headed mode for initial authentication.
