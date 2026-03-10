import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

# Relative imports
from .core.browser import browser_manager
from .core.pdf import create_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("readly-mcp")

# Initialize FastMCP
mcp = FastMCP(
    name="Readly Scraper",
    instructions="MCP server for scraping Readly magazines and generating PDFs",
    version="0.1.0",
)

# Global ephemeral state
scraping_state: dict[str, Any] = {
    "is_running": False,
    "current_page": 0,
    "issue_name": "",
    "screenshots": [],
    "status": "Idle",
    "stop_flag": False,
}


async def scraping_worker(issue_name: str, duration_per_page: float, max_pages: int):
    """
    Background worker that performing the scraping loop.
    """
    global scraping_state

    logger.info(f"Starting scrape for {issue_name}...")
    scraping_state["status"] = "Running"
    scraping_state["screenshots"] = []
    scraping_state["current_page"] = 0
    scraping_state["stop_flag"] = False

    try:
        # 1. Ensure browser is open
        await browser_manager.start_browser(headless=False)

        last_screenshot_path = None

        for i in range(1, max_pages + 1):
            if scraping_state["stop_flag"]:
                logger.info("Scraping stopped by user.")
                break

            scraping_state["current_page"] = i

            # 2. Capture Page
            logger.info(f"Capturing page {i}...")
            screenshot_path = await browser_manager.take_page_screenshot(issue_name, i)

            # 3. Simple Duplicate Check (End of Issue Detection)
            if last_screenshot_path:
                try:
                    with (
                        open(screenshot_path, "rb") as f1,
                        open(last_screenshot_path, "rb") as f2,
                    ):
                        if f1.read() == f2.read():
                            logger.info("Page identical to previous one. End of issue detected.")
                            os.remove(screenshot_path)
                            break
                except FileNotFoundError:
                    pass

            scraping_state["screenshots"].append(screenshot_path)
            last_screenshot_path = screenshot_path

            # 4. Wait (Simulate Reading)
            logger.info(f"Reading page {i} for {duration_per_page} seconds...")
            slept = 0
            while slept < duration_per_page:
                if scraping_state["stop_flag"]:
                    break
                await asyncio.sleep(1)
                slept += 1

            if scraping_state["stop_flag"]:
                break

            # 5. Turn Page
            logger.info("Turning page...")
            await browser_manager.turn_page_right()

            # Wait for animation/load
            await asyncio.sleep(2)

        # 6. Compile PDF
        if scraping_state["screenshots"]:
            logger.info("Compiling PDF...")
            scraping_state["status"] = "Compiling PDF"

            pdf_name = f"{issue_name}_full.pdf"
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "readly")
            if not os.path.exists(desktop_path):
                os.makedirs(desktop_path)

            output_path = os.path.join(desktop_path, pdf_name)
            create_pdf(scraping_state["screenshots"], output_path)

            logger.info(f"Done! PDF saved to {output_path}")
            scraping_state["status"] = "Completed"
        else:
            logger.info("No screenshots captured.")
            scraping_state["status"] = "Failed: No pages captured"

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        scraping_state["status"] = f"Error: {str(e)}"
    finally:
        scraping_state["is_running"] = False


# --- MCP Tools ---


@mcp.tool()
async def open_readly_browser() -> str:
    """Opens the browser and navigates to Readly. Use this first to log in manually."""
    await browser_manager.start_browser(headless=False)
    await browser_manager.go_to_readly()
    return "Browser opened. Please log in and navigate to the issue you want to scrape."


@mcp.tool()
async def smart_scrape(issue_name: str, interval_seconds: int = 120, max_pages: int = 200) -> str:
    """Starts the scraping process in the background."""
    if scraping_state["is_running"]:
        return "Error: A scraping job is already running."

    scraping_state["is_running"] = True
    scraping_state["issue_name"] = issue_name
    scraping_state["stop_flag"] = False

    asyncio.create_task(scraping_worker(issue_name, interval_seconds, max_pages))
    return f"Started scraping '{issue_name}'. Use 'get_status' to check progress."


@mcp.tool()
def get_status() -> dict:
    """Returns the current status of the scraping job."""
    return {
        "status": scraping_state["status"],
        "is_running": scraping_state["is_running"],
        "issue": scraping_state["issue_name"],
        "current_page": scraping_state["current_page"],
        "pages_captured": len(scraping_state["screenshots"]),
    }


@mcp.tool()
def stop_scrape() -> str:
    """Stops the current scraping job gracefully."""
    if not scraping_state["is_running"]:
        return "No job running."
    scraping_state["stop_flag"] = True
    return "Stop signal sent."


# --- FastAPI API Bridge ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Readly MCP API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
async def api_get_status():
    return get_status()


@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "version": "0.1.0", "mcp_connected": True}


@app.get("/api/tools")
async def api_list_tools():
    return [{"name": t.name, "description": t.description} for t in mcp.tools]


@app.post("/api/scrape/start")
async def api_start_scrape(issue_name: str, interval: int = 120, max_pages: int = 200):
    res = await smart_scrape(issue_name, interval, max_pages)
    if res.startswith("Error"):
        raise HTTPException(status_code=400, detail=res)
    return {"message": res}


@app.post("/api/scrape/stop")
async def api_stop_scrape():
    return {"message": stop_scrape()}


def main():
    from .transport import run_server

    # Check for --web flag
    if "--web" in sys.argv:
        port = int(os.getenv("WEB_PORT", 10863))
        logger.info(f"Starting FastAPI Web Bridge on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Standard MCP runner
        run_server(mcp, server_name="readly-mcp")


if __name__ == "__main__":
    main()
