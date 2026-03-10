import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Literal, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from browser import browser_manager
from pdf_maker import create_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("readly-mcp")

# Initialize FastMCP
mcp = FastMCP("Readly Scraper")

# Global state
scraping_state = {
    "is_running": False,
    "current_page": 0,
    "issue_name": "",
    "screenshots": [],
    "status": "Idle",
    "stop_flag": False,
}


def scraping_worker(issue_name: str, duration_per_page: float, max_pages: int):
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
        # We assume the user has already navigated to the reader view
        page = browser_manager.start_browser(headless=False)

        last_screenshot_path = None

        for i in range(1, max_pages + 1):
            if scraping_state["stop_flag"]:
                logger.info("Scraping stopped by user.")
                break

            scraping_state["current_page"] = i

            # 2. Take Screenshot
            logger.info(f"Capturing page {i}...")
            screenshot_path = browser_manager.take_page_screenshot(issue_name, i)

            # 3. Check for duplicates (End of Issue Detection)
            if last_screenshot_path:
                with (
                    open(screenshot_path, "rb") as f1,
                    open(last_screenshot_path, "rb") as f2,
                ):
                    if f1.read() == f2.read():
                        logger.info("Page identical to previous one. End of issue detected.")
                        # Remove duplicate
                        os.remove(screenshot_path)
                        break

            scraping_state["screenshots"].append(screenshot_path)
            last_screenshot_path = screenshot_path

            # 4. Wait (Simulate Reading)
            logger.info(f"Reading page {i} for {duration_per_page} seconds...")
            slept = 0
            while slept < duration_per_page:
                if scraping_state["stop_flag"]:
                    break
                time.sleep(1)
                slept += 1

            if scraping_state["stop_flag"]:
                break

            # 5. Turn Page
            logger.info("Turning page...")
            browser_manager.turn_page_right()

            # Wait for animation
            time.sleep(2)

        # 6. Compile PDF
        logger.info("Compiling PDF...")
        scraping_state["status"] = "Compiling PDF"

        pdf_name = f"{issue_name}_full.pdf"
        output_path = os.path.join(os.getcwd(), pdf_name)
        create_pdf(scraping_state["screenshots"], output_path)

        logger.info(f"Done! PDF saved to {output_path}")
        scraping_state["status"] = "Completed"

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        scraping_state["status"] = f"Error: {str(e)}"
    finally:
        scraping_state["is_running"] = False


# FastAPI Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure browser manager or other components are ready if needed
    yield
    # Shutdown: Cleanup if needed


app = FastAPI(title="Readly MCP API", lifespan=lifespan)

# Add CORS for SOTA Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend port 10862
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "readly-mcp"}


@app.get("/api/status")
async def get_status():
    return {
        "status": scraping_state["status"],
        "is_running": scraping_state["is_running"],
        "issue": scraping_state["issue_name"],
        "current_page": scraping_state["current_page"],
        "pages_captured": len(scraping_state["screenshots"]),
    }


@app.post("/api/scrape/start")
async def start_scrape(issue_name: str, interval: int = 120, max_pages: int = 200):
    if scraping_state["is_running"]:
        raise HTTPException(status_code=400, detail="A scraping job is already running")

    scraping_state["is_running"] = True
    scraping_state["issue_name"] = issue_name

    t = threading.Thread(target=scraping_worker, args=(issue_name, interval, max_pages))
    t.start()

    return {"message": f"Started scraping '{issue_name}'"}


@app.post("/api/scrape/stop")
async def stop_scrape():
    if not scraping_state["is_running"]:
        return {"message": "No job running"}

    scraping_state["stop_flag"] = True
    return {"message": "Stop signal sent"}


@app.get("/api/tools")
async def list_tools():
    """Expose MCP tools to the SOTA UI."""
    return [{"name": tool.name, "description": tool.description} for tool in mcp.tools]


# Original MCP Tools
@mcp.tool()
def open_readly_browser():
    """
    Opens the browser and navigates to Readly.
    Use this to log in manually securely.
    """
    browser_manager.start_browser(headless=False)
    browser_manager.go_to_readly()
    return "Browser opened. Please log in and navigate to the issue you want to scrape."


@mcp.tool()
def start_scraping_issue(issue_name: str, interval_seconds: int = 120, max_pages: int = 200):
    """
    Starts the scraping process in the background.

    Args:
        issue_name: Name of the magazine (used for filenames).
        interval_seconds: How long to stay on each page (default 120s/2min).
        max_pages: Safety limit for pages (default 200).
    """
    return threading.Thread(
        target=start_scrape,
        kwargs={"issue_name": issue_name, "interval": interval_seconds, "max_pages": max_pages},
    ).run()  # This logic is now in the worker, but for MCP compatibility we wrap it.


@mcp.tool()
def get_scraping_status_tool():
    """Returns the current status of the scraping job."""
    return scraping_state


@mcp.tool()
def stop_scraping_tool():
    """Stops the current scraping job gracefully."""
    scraping_state["stop_flag"] = True
    return "Stop signal sent."


if __name__ == "__main__":
    port = int(os.getenv("WEB_PORT", 10863))
    uvicorn.run(app, host="0.0.0.0", port=port)
