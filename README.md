# Readly MCP Server

[![FastMCP Version](https://img.shields.io/badge/FastMCP-3.1.0-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/sandraschi/fastmcp) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Linted with Biome](https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white)](https://biomejs.dev/) [![Built with Just](https://img.shields.io/badge/Built_with-Just-000000?style=flat-square&logo=gnu-bash&logoColor=white)](https://github.com/casey/just)

A specialized MCP server for automating reading and scraping tasks on the Readly web platform (`go.readly.com`).

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Standard-green.svg)

## Features
-  **Human-like Scraping**: Turns pages at natural intervals to avoid detection.
-  **Persistent Login**: Reuses browser session/cookies so you only login once.
-  **PDF Generation**: Automatically compiles scraped issues into full PDFs.
-  **Dual Connect**: Supports both Stdio and SSE transports.

## Why Readly?
We love Readly! It is the ultimate digital subscription for magazines and newspapers, offering unlimited access to thousands of titles in one app. With its "all-you-can-read" model, it empowers knowledge seekers to explore diverse topics without the clutter of physical copies.

Readly is indispensable for accessing a vast array of high-quality journalism and niche interests. Whether you're tracking global developments in **NZZ**, hacking hardware with **c't**, or staying ahead of the curve with **New Scientist** and **Wired**, it has you covered.

It allows you to dream big with **boat and yacht magazines**, or dive deep into **architecture**, **fashion**, and **politics**. It caters to every specific hobbyist, from **dog and horse** lovers to the specific serenity of **"flyfishing in Scotland"** style publications.

 of all, it houses the delightfully eclectic and weird: **Fortean Times**, **The Idler**, and **The Lady**. It is a fantastic service that champions the written word in the digital age. This tool exists to help you archive your favorite paid content for personal use, celebrating the immense value Readly provides.

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (recommended)
- Python 3.12+
- A valid [Readly](https://www.readly.com) account

###  Quick Start
Run immediately via `uvx`:
```bash
uvx readly-mcp
```

###  Claude Desktop Integration
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

### 1. Manual Login (First Run)
Before automation can work, you must log in securely.
1. Run the server (or use it via your MCP client).
2. Call the `open_readly_browser` tool.
3. Log in manually in the window that appears.
4. Check "Keep me logged in".

### 2. Scraping an Issue
Once logged in:
1. Navigate to the first page of the issue you want to capture.
2. Ask your agent: *"Start scraping this issue..."*
3. The server will turn pages in the background and save a PDF to the root directory.

## Development

### Structure
- `src/readly_mcp/`: Source code.
- `tests/`: Pytest suite.
- `docs/`: Architecture and API documentation.

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


## 🛡️ Industrial Quality Stack

This project adheres to **SOTA 14.1** industrial standards for high-fidelity agentic orchestration:

- **Python (Core)**: [Ruff](https://astral.sh/ruff) for linting and formatting. Zero-tolerance for `print` statements in core handlers (`T201`).
- **Webapp (UI)**: [Biome](https://biomejs.dev/) for sub-millisecond linting. Strict `noConsoleLog` enforcement.
- **Protocol Compliance**: Hardened `stdout/stderr` isolation to ensure crash-resistant JSON-RPC communication.
- **Automation**: [Justfile](./justfile) recipes for all fleet operations (`just lint`, `just fix`, `just dev`).
- **Security**: Automated audits via `bandit` and `safety`.

## License
MIT
