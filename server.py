import time
import threading
import os
from fastmcp import FastMCP
from typing import Optional

from browser import browser_manager
from pdf_maker import create_pdf

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

    print(f"Starting scrape for {issue_name}...")
    scraping_state["status"] = "Running"
    scraping_state["screenshots"] = []
    scraping_state["current_page"] = 0
    scraping_state["stop_flag"] = False

    try:
        # 1. Ensure browser is open
        page = browser_manager.start_browser(headless=False)
        # We assume the user has already navigated to the reader view

        last_screenshot_path = None

        for i in range(1, max_pages + 1):
            if scraping_state["stop_flag"]:
                print("Scraping stopped by user.")
                break

            scraping_state["current_page"] = i

            # 2. Take Screenshot
            print(f"Capturing page {i}...")
            screenshot_path = browser_manager.take_page_screenshot(issue_name, i)

            # 3. Check for duplicates (End of Issue Detection)
            # Simple file size check or just rely on 'next' not working?
            # Let's rely on the user stopping it or max_pages for now,
            # as determining visual equality is expensive without extra libs.
            # But we can check if the file content is IDENTICAL to the last one.
            if last_screenshot_path:
                with (
                    open(screenshot_path, "rb") as f1,
                    open(last_screenshot_path, "rb") as f2,
                ):
                    if f1.read() == f2.read():
                        print("Page identical to previous one. End of issue detected.")
                        # Remove duplicate
                        os.remove(screenshot_path)
                        break

            scraping_state["screenshots"].append(screenshot_path)
            last_screenshot_path = screenshot_path

            # 4. Wait (Simulate Reading)
            print(f"Reading page {i} for {duration_per_page} seconds...")
            # We accept a stop signal during the wait
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

            # Wait for animation
            time.sleep(2)

        # 6. Compile PDF
        print("Compiling PDF...")
        scraping_state["status"] = "Compiling PDF"

        pdf_name = f"{issue_name}_full.pdf"
        output_path = os.path.join(os.getcwd(), pdf_name)
        create_pdf(scraping_state["screenshots"], output_path)

        print(f"Done! PDF saved to {output_path}")
        scraping_state["status"] = "Completed"

    except Exception as e:
        print(f"Error during scraping: {e}")
        scraping_state["status"] = f"Error: {str(e)}"
    finally:
        scraping_state["is_running"] = False


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
def start_scraping_issue(
    issue_name: str, interval_seconds: int = 120, max_pages: int = 200
):
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
def get_scraping_status():
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
def stop_scraping():
    """
    Stops the current scraping job gracefully.
    """
    if not scraping_state["is_running"]:
        return "No job running."

    scraping_state["stop_flag"] = True
    return "Stop signal sent. Job will terminate after the current pending wait."


if __name__ == "__main__":
    mcp.run()
