import time
import threading
import os
import shutil
from typing import Optional
from fastmcp import FastMCP

# Relative imports
from .core.browser import browser_manager
from .core.pdf import create_pdf

# Initialize FastMCP
mcp = FastMCP("Readly Scraper", dependencies=["playwright", "fpdf2", "Pillow"])

# Global ephemeral state
# In a rigorous production env, this might be a class or database,
# but for a single-user local tool, a global dict is sufficient.
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

    print(f"Starting scrape for {issue_name}...")
    scraping_state["status"] = "Running"
    scraping_state["screenshots"] = []
    scraping_state["current_page"] = 0
    scraping_state["stop_flag"] = False

    try:
        # 1. Ensure browser is open
        # The user must have already navigated to the issue in open_readly_browser
        browser_manager.start_browser(headless=False)

        last_screenshot_path = None

        # Start from page 1
        for i in range(1, max_pages + 1):
            if scraping_state["stop_flag"]:
                print("Scraping stopped by user.")
                break

            scraping_state["current_page"] = i

            # 2. Capture Page
            print(f"Capturing page {i}...")
            # We assume the browser is currently ON the correct page.
            screenshot_path = browser_manager.take_page_screenshot(issue_name, i)

            # 3. Simple Duplicate Check (End of Issue Detection)
            if last_screenshot_path:
                try:
                    with (
                        open(screenshot_path, "rb") as f1,
                        open(last_screenshot_path, "rb") as f2,
                    ):
                        if f1.read() == f2.read():
                            print(
                                "Page identical to previous one. End of issue detected."
                            )
                            os.remove(screenshot_path)
                            break
                except FileNotFoundError:
                    pass

            scraping_state["screenshots"].append(screenshot_path)
            last_screenshot_path = screenshot_path

            # 4. Wait (Simulate Reading)
            print(f"Reading page {i} for {duration_per_page} seconds...")
            slept = 0
            while slept < duration_per_page:
                if scraping_state["stop_flag"]:
                    break
                time.sleep(1)
                slept += 1

            if scraping_state["stop_flag"]:
                break

            # 5. Turn Page
            print("Turning page...")
            browser_manager.turn_page_right()

            # Wait for animation/load
            time.sleep(2)

        # 6. Compile PDF
        if scraping_state["screenshots"]:
            print("Compiling PDF...")
            scraping_state["status"] = "Compiling PDF"

            pdf_name = f"{issue_name}_full.pdf"
            # Save to Desktop/readly as requested
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "readly")
            if not os.path.exists(desktop_path):
                os.makedirs(desktop_path)

            output_path = os.path.join(desktop_path, pdf_name)
            create_pdf(scraping_state["screenshots"], output_path)

            print(f"Done! PDF saved to {output_path}")
            scraping_state["status"] = "Completed"
        else:
            print("No screenshots captured.")
            scraping_state["status"] = "Failed: No pages captured"

    except Exception as e:
        print(f"Error during scraping: {e}")
        scraping_state["status"] = f"Error: {str(e)}"
    finally:
        scraping_state["is_running"] = False


@mcp.tool()
def open_readly_browser() -> str:
    """
    Opens the browser and navigates to Readly.
    Use this first to log in manually and select the magazine.
    """
    browser_manager.start_browser(headless=False)
    browser_manager.go_to_readly()
    return "Browser opened. Please log in and navigate to the issue you want to scrape."


@mcp.tool()
def smart_scrape(
    issue_name: str, interval_seconds: int = 120, max_pages: int = 200
) -> str:
    """
    Starts the scraping process in the background.

    Args:
        issue_name: Name of the magazine (used for filenames).
        interval_seconds: How long to stay on each page (default 120s/2min).
        max_pages: Safety limit for pages (default 200).
    """
    if scraping_state["is_running"]:
        return "Error: A scraping job is already running."

    scraping_state["is_running"] = True
    scraping_state["issue_name"] = issue_name

    t = threading.Thread(
        target=scraping_worker, args=(issue_name, interval_seconds, max_pages)
    )
    t.start()

    return f"Started scraping '{issue_name}'. I will turn the page every {interval_seconds} seconds. Use 'get_scraping_status' to check progress."


@mcp.tool()
def get_status() -> dict:
    """
    Returns the current status of the scraping job.
    """
    return {
        "status": scraping_state["status"],
        "is_running": scraping_state["is_running"],
        "issue": scraping_state["issue_name"],
        "current_page": scraping_state["current_page"],
        "pages_captured": len(scraping_state["screenshots"]),
    }


@mcp.tool()
def stop_scrape() -> str:
    """
    Stops the current scraping job gracefully.
    """
    if not scraping_state["is_running"]:
        return "No job running."

    scraping_state["stop_flag"] = True
    return "Stop signal sent. Job will terminate after the current pending wait."
