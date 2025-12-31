# Product Requirements Document (PRD): Readly MCP Server

## 1. Overview
The **Readly MCP Server** is a specialized Model Context Protocol (MCP) server designed to bridge the gap between Large Language Models (LLMs) and the Readly digital magazine platform (`go.readly.com`). It allows AI agents to read, scrape, and archive magazine issues by simulating human interaction within a browser environment.

## 2. Goals & Objectives
- **Automated Access**: Enable LLMs to access magazine content that doesn't have a public API.
- **Human Simulation**: Mimic human reading behavior (page turning intervals) to avoid bot detection and rate limiting.
- **Archival**: Convert transient web content into persistent PDF documents for downstream processing or offline reading.
- **Integration**: Provide a standard MCP interface for seamless integration with tools like Claude Desktop, Cursor, and other MCP clients.

## 3. Core Features

### 3.1 Browser Management
- **Persistent Context**: Store user session data (cookies, local storage) to maintain login state across server restarts.
- **Headless & Headed Modes**: Support both headless operation for background tasks and headed mode for initial manual login/debugging.

### 3.2 Scraping Engine
- **Page Navigation**: Automate "next page" actions using keyboard or mouse simulation.
- **Screenshot Capture**: High-resolution viewport capture of each page.
- **Anti-Detection**: Configurable delays and human-like interactions.

### 3.3 Output Generation
- **PDF Compilation**: Stitch captured artifacts into a single, specialized PDF file.
- **Cleanup**: Automatic removal of temporary artifacts after successful compilation.

## 4. Architecture
- **Framework**: fastmcp (v2.14.1+)
- **Transport**: Stdio (primary) & SSE/HTTP (capability)
- **Engine**: Playwright (Synchronous API)
- **Image Processing**: Pillow & FPDF2

## 5. Constraints & Assumptions
- **User Account**: A valid, paid Readly account is required.
- **Local Execution**: The server runs locally on the user's machine to leverage their IP and credentials.
- **Rate Limits**: Implicitly limited by the "human speed" constraints to prevent account banning.
