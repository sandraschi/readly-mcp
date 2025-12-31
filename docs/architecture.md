# Architecture

## System Overview

The **Readly MCP Server** is built on a layered architecture to separate concerns between the MCP interface, the browser automation engine, and the file processing logic.

### Layers

1.  **Interface Layer (`server.py`)**
    - Uses `fastmcp` to define tools and resources.
    - Manages the `scraping_state` (global ephemeral state).
    - Handles identifying and dispatching background threads for long-running scrape jobs.

2.  **Core Logic Layer (`core/`)**
    - **Browser Manager (`browser.py`)**: Singleton class wrapping `playwright`.
        - Manages `BrowserContext` persistence in `./user_data`.
        - Handles viewport management and event simulation.
    - **PDF Engine (`pdf.py`)**:
        - Wraps `fpdf2` and `Pillow`.
        - Handles image ingestion and document assembly.

3.  **Infrastructure**
    - **FileSystem**: Stores screenshots temporarily in `./screenshots/` and persistent data in `./user_data/`.
    - **Network**: Connects to `go.readly.com` via Chromium.

## Data Flow

1.  **Request**: User invokes `smart_scrape` via MCP.
2.  **State Update**: Server sets `is_running=True` and spawns a `threading.Thread`.
3.  **Execution LOOP**:
    - Browser takes screenshot -> `fs`.
    - Sleep interval.
    - Browser simulates "ArrowRight".
4.  **Completion**:
    - PDF Engine reads `fs` screenshots.
    - Generates `.pdf` file.
    - Cleans up screenshots (optional/future).
