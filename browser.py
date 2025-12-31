import os
import time
from playwright.sync_api import sync_playwright, BrowserContext, Page

USER_DATA_DIR = os.path.join(os.getcwd(), "user_data")
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def start_browser(self, headless=False):
        """
        Starts the Playwright browser with a persistent context.
        """
        if self.context:
            return self.context

        print(f"Starting browser (Headless: {headless})...")
        self.playwright = sync_playwright().start()

        # Ensure user data dir exists
        if not os.path.exists(USER_DATA_DIR):
            os.makedirs(USER_DATA_DIR)

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless,
            viewport={"width": 1920, "height": 1080},  # Good resolution for reading
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-GB",
        )

        # Open a new page or get existing one
        pages = self.context.pages
        if pages:
            self.page = pages[0]
        else:
            self.page = self.context.new_page()

        return self.page

    def go_to_readly(self):
        if not self.page:
            self.start_browser(headless=False)
        self.page.goto("https://go.readly.com")

    def take_page_screenshot(self, issue_name: str, page_num: int) -> str:
        """
        Takes a screenshot of the current viewport.
        Returns the path to the screenshot.
        """
        if not self.page:
            raise RuntimeError("Browser not started")

        # Create issue specific dir
        issue_safe_name = "".join(
            [c for c in issue_name if c.isalnum() or c in (" ", "-", "_")]
        ).strip()
        save_dir = os.path.join(SCREENSHOTS_DIR, issue_safe_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filename = f"page_{page_num:03d}.png"
        filepath = os.path.join(save_dir, filename)

        # We might want to hide UI elements here if possible, but Readly's fullscreen
        # usually hides them after a moment of inactivity.
        # Moving mouse to corner to avoid hover effects
        self.page.mouse.move(0, 0)
        time.sleep(0.5)

        self.page.screenshot(
            path=filepath, full_page=False
        )  # Viewport only is usually better for "what the user sees"
        return filepath

    def turn_page_right(self):
        if not self.page:
            raise RuntimeError("Browser not started")

        # Method 1: Keyboard
        self.page.keyboard.press("ArrowRight")

        # Method 2: Click right side of screen (fallback)
        # width = self.page.viewport_size['width']
        # height = self.page.viewport_size['height']
        # self.page.mouse.click(width - 50, height / 2)

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        self.context = None
        self.page = None
        self.playwright = None


# Global instance
browser_manager = BrowserManager()
