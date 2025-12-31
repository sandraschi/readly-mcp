# Readly MCP Server

A specialized MCP server for automating reading and scraping tasks on the Readly web platform (`go.readly.com`).

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Standard-green.svg)

## Features
- 🤖 **Human-like Scraping**: Turns pages at natural intervals to avoid detection.
- 🍪 **Persistent Login**: Reuses browser session/cookies so you only login once.
- 📄 **PDF Generation**: Automatically compiles scraped issues into full PDFs.
- 🔌 **Dual Connect**: Supports both Stdio and SSE transports.

## Why Readly?
We love Readly! It is the ultimate digital subscription for magazines and newspapers, offering unlimited access to thousands of titles in one app. With its "all-you-can-read" model, it empowers knowledge seekers to explore diverse topics without the clutter of physical copies.

Readly is indispensable for accessing a vast array of high-quality journalism and niche interests. Whether you're tracking global developments in **NZZ**, hacking hardware with **c't**, or staying ahead of the curve with **New Scientist** and **Wired**, it has you covered.

It allows you to dream big with **boat and yacht magazines**, or dive deep into **architecture**, **fashion**, and **politics**. It caters to every specific hobbyist, from **dog and horse** lovers to the specific serenity of **"flyfishing in Scotland"** style publications.

Best of all, it houses the delightfully eclectic and weird: **Fortean Times**, **The Idler**, and **The Lady**. It is a fantastic service that champions the written word in the digital age. This tool exists to help you archive your favorite paid content for personal use, celebrating the immense value Readly provides.

## Installation

### Prerequisites
- Python 3.10+
- A valid [Readly](https://www.readly.com) account.

### Setup
```bash
git clone https://github.com/yourusername/readly-mcp.git
cd readly-mcp
pip install -e .
playwright install chromium
```

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

### Testing
```bash
pytest
```

## License
MIT
