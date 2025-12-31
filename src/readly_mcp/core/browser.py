import os
import time
import asyncio
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright

# Determine paths relative to where the server runs (usually repo root)
# Ideally, we should allow configuration or usage of standard app data paths.
# For this specific user request (local operation), CWD is acceptable request.
USER_DATA_DIR = os.path.join(os.getcwd(), "user_data")
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")


class BrowserManager:
    """
    Manages a persistent Playwright session using async API.
    """

    def __init__(self):
        self.playwright: Playwright | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self._lock: asyncio.Lock | None = None
    
    def _get_lock(self):
        """Get or create the lock."""
        if self._lock is None:
            try:
                self._lock = asyncio.Lock()
            except RuntimeError:
                # If no event loop exists, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self._lock = asyncio.Lock()
        return self._lock

    async def start_browser(self, headless=False):
        """
        Starts the Playwright browser with a persistent context.
        """
        lock = self._get_lock()
        async with lock:
            if self.context:
                try:
                    # Check if context is still valid
                    pages = self.context.pages
                    if pages:
                        return self.page
                except Exception:
                    # Context seemingly dead, restart
                    await self.close()

            print(f"Starting browser (Headless: {headless})...")
            self.playwright = await async_playwright().start()

            if not os.path.exists(USER_DATA_DIR):
                os.makedirs(USER_DATA_DIR)

            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=headless,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="en-GB",
                # Grant permissions if needed
                permissions=["clipboard-read", "clipboard-write"],
            )

            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.context.new_page()

            return self.page

    async def go_to_readly(self):
        if not self.page:
            await self.start_browser(headless=False)
        await self.page.goto("https://go.readly.com")

    async def take_page_screenshot(self, issue_name: str, page_num: int) -> str:
        """
        Takes a screenshot of the current viewport.
        Returns the absolute path to the screenshot.
        """
        if not self.page:
            raise RuntimeError("Browser not started")

        # Sanitize issue name for directory usage
        issue_safe_name = "".join(
            [c for c in issue_name if c.isalnum() or c in (" ", "-", "_")]
        ).strip()
        save_dir = os.path.join(SCREENSHOTS_DIR, issue_safe_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filename = f"page_{page_num:03d}.png"
        filepath = os.path.join(save_dir, filename)

        # Reset mouse to avoid hover overlays
        try:
            await self.page.mouse.move(0, 0)
        except Exception:
            pass  # Ignore if move fails

        await asyncio.sleep(0.5)

        await self.page.screenshot(path=filepath, full_page=False)
        return filepath

    async def turn_page_right(self):
        if not self.page:
            raise RuntimeError("Browser not started")

        # Press Right Arrow
        await self.page.keyboard.press("ArrowRight")

    async def close(self):
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Error closing browser: {e}")
        finally:
            self.context = None
            self.page = None
            self.playwright = None


# Global instance for the application
browser_manager = BrowserManager()
