# Readly MCP Server

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — quick start, manual setup, and troubleshooting

A specialized MCP server for automated reading, scraping, and content extraction on the Readly digital magazine platform (`go.readly.com`).

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Standard-green.svg)

## Features

- **Content Intelligence (v0.2)**: Extract article titles, URLs, and full text from magazine issues
- **Magazine Search (v0.2)**: Search Readly's catalog for magazines by keyword
- **Human-like Scraping**: Turns pages at natural intervals to avoid detection.
- **Persistent Login**: Reuses browser session/cookies so you only login once.
- **PDF Generation**: Automatically compiles scraped issues into full PDFs.
- **Dual Transport**: Supports Stdio, HTTP Streamable, and SSE transports.
- **REST API**: FastAPI bridge for integration with fleet servers (e.g. `aiwatcher-mcp`).

## Why Readly?

We love Readly! It is the ultimate digital subscription for magazines and newspapers, offering unlimited access to thousands of titles in one app. With its "all-you-can-read" model, it empowers knowledge seekers to explore diverse topics without the clutter of physical copies.

Readly is indispensable for accessing a vast array of high-quality journalism and niche interests. Whether you're tracking global developments in **NZZ**, hacking hardware with **c't**, or staying ahead of the curve with **New Scientist** and **Wired**, it has you covered.

It allows you to dream big with **boat and yacht magazines**, or dive deep into **architecture**, **fashion**, and **politics**. It caters to every specific hobbyist, from **dog and horse** lovers to the specific serenity of **"flyfishing in Scotland"** style publications.

Best of all, it houses the delightfully eclectic and weird: **Fortean Times**, **The Idler**, and **The Lady**. It is a fantastic service that champions the written word in the digital age. This tool exists to help you archive your favorite paid content for personal use, celebrating the immense value Readly provides.

## Quick Start

```powershell
git clone https://github.com/sandraschi/readly-mcp
cd readly-mcp
just
```

This opens an interactive dashboard showing all available commands. Run `just bootstrap` to install dependencies, then `just serve` or `just dev` to start.

### Manual Setup

If you don't have `just` installed:


## Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (recommended)
- Python 3.12+
- A valid [Readly](https://www.readly.com) account

### Quick Start
Run immediately via `uvx`:
```bash
uvx readly-mcp
```

### Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "readly-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/readly-mcp", "run", "readly-mcp"]
  }
}
```

### Setup (from source)
```bash
git clone https://github.com/sandraschi/readly-mcp.git
cd readly-mcp
uv sync
playwright install chromium
```
Key dependencies: FastMCP, FastAPI, uvicorn, Playwright, fpdf2, Pillow (see `pyproject.toml`).

## Usage

### 1. Auto-Login (Recommended)
Set your Readly auth token from the browser's Application cookies as an environment variable:
```bash
set READLY_AUTH_TOKEN=eyJhbGciOiJSUzI1...
```
Or paste it via the Settings page in the web dashboard. The token is sent to the
backend via `POST /api/auth/token` and used to set the `readlyAuth` cookie
automatically when `open_readly_browser` is called — no manual login needed.

### 2. Manual Login (Fallback)
If no token is available, the first run requires manual login (cookies are persisted):
1. Call the `open_readly_browser` tool.
2. Log in manually in the window that appears.
3. Future sessions reuse these cookies automatically.

### 3. Content Intelligence (v0.2)
Once logged in and on a magazine issue page:
- **List articles**: `list_articles` — extracts all article titles and URLs from the current page
- **Read article**: `extract_article_text` — click an article and extract its full text
- **Search catalog**: `search_magazines` — find magazines by keyword

### 4. Scraping an Issue
Once logged in:
1. Navigate to the first page of the issue you want to capture.
2. Call: `smart_scrape` with the issue name, interval, and max pages.
3. The server will turn pages in the background and save a PDF to `~/Desktop/readly/`.

## MCP Tools

| Tool | Category | Description |
|------|----------|-------------|
| `open_readly_browser` | Browser | Open browser, log in manually |
| `list_articles` | Content (v0.2) | Extract article titles + URLs from current magazine page |
| `extract_article_text` | Content (v0.2) | Click an article and extract full text content |
| `search_magazines` | Content (v0.2) | Search Readly catalog by keyword |
| `smart_scrape` | Scraping | Page-by-page screenshot + PDF compilation |
| `get_status` | Status | Current scraping job status |
| `stop_scrape` | Control | Gracefully stop scraping job |

## REST API (port 10863, via `--web` flag)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/status` | Scraping job status |
| `GET` | `/api/tools` | List registered MCP tools |
| `GET` | `/api/articles/list` | List articles on current page |
| `GET` | `/api/articles/extract?index=N` | Extract article text by index |
| `GET` | `/api/magazines/search?q=QUERY` | Search magazines by keyword |
| `POST` | `/api/scrape/start` | Start scraping job |
| `POST` | `/api/scrape/stop` | Stop scraping job |

## Development

### Structure
- `src/readly_mcp/`: Source code (server, browser manager, PDF generation, transport)
- `tests/`: Pytest suite
- `docs/`: Architecture and API documentation

### Running the HTTP/SSE server
For web or SSE transport (FastAPI + uvicorn):
```bash
uv run readly-mcp --web
```
Uses `WEB_PORT` (default 10863). Requires FastAPI and uvicorn (included in dependencies).

### Testing
```bash
pytest
```

### Integration with aiwatcher-mcp
readly-mcp v0.2+ serves as a content intelligence source for aiwatcher-mcp.
Set `READLY_ENABLED=true` and `READLY_MCP_URL=http://localhost:10863` in aiwatcher-mcp's `.env`.

## Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License
MIT
