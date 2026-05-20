import asyncio
import os

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

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

        token = os.environ.get("READLY_AUTH_TOKEN", "")
        domain = os.environ.get("READLY_DOMAIN", "www.readly.co")

        auth_url = f"https://{domain}/at/newsstand"
        if token:
            auth_url = f"{auth_url}?readlyAuth={token}"

        await self.page.goto(auth_url)

    async def _auto_login(self, domain: str, token: str) -> None:
        """Set the Readly auth cookie before navigating — skips manual login."""
        if not self.context:
            return
        try:
            await self.context.add_cookies([
                {
                    "name": "readlyAuth",
                    "value": token,
                    "domain": domain,
                    "path": "/",
                    "secure": True,
                    "httpOnly": True,
                }
            ])
            logger = __import__("logging").getLogger("readly-mcp")
            logger.info("Auto-login: readlyAuth cookie set for %s", domain)
        except Exception as exc:
            logger = __import__("logging").getLogger("readly-mcp")
            logger.warning("Auto-login failed: %s", exc)

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

    async def list_articles(self) -> dict:
        """Parse the current Readly magazine page DOM to extract article titles and URLs."""
        if not self.page:
            raise RuntimeError("Browser not started")

        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(1.5)

        page_title = await self.page.title()

        articles = await self.page.evaluate("""() => {
            const results = [];
            const seen = new Set();
            // Try multiple selector strategies for Readly's article cards
            const selectors = [
                'a[href*="/read/"]',
                'a[href*="article"]',
                '[class*="track"] a',
                '[class*="article"] a',
                '[data-testid*="article"]',
                'article a',
                '.issue-page a'
            ];
            for (const sel of selectors) {
                for (const el of document.querySelectorAll(sel)) {
                    const text = el.textContent.trim();
                    const href = el.href || '';
                    if (text.length > 10 && !seen.has(href) && (href.includes('readly.co') || href.includes('readly.com'))) {
                        seen.add(href);
                        results.push({title: text.substring(0, 200), url: href});
                    }
                }
                if (results.length >= 3) break;
            }
            // Fallback: grab any meaningful headings
            if (results.length === 0) {
                for (const h of document.querySelectorAll('h1,h2,h3,h4')) {
                    const text = h.textContent.trim();
                    if (text.length > 10) results.push({title: text, url: ''});
                }
            }
            return results;
        }""")

        return {
            "issue_title": page_title,
            "page_url": self.page.url,
            "articles": [{"title": a["title"], "url": a["url"], "index": i} for i, a in enumerate(articles)],
            "count": len(articles),
        }

    async def extract_article_text(self, article_index: int = 0) -> dict:
        """Navigate to an article and extract its full text content."""
        if not self.page:
            raise RuntimeError("Browser not started")

        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(1.5)

        # Find the article link by index
        href = await self.page.evaluate(f"""((index) => {{
            const results = [];
            const seen = new Set();
            const selectors = [
                'a[href*="/read/"]',
                'a[href*="article"]',
                '[class*="track"] a',
                '[class*="article"] a',
            ];
            for (const sel of selectors) {{
                for (const el of document.querySelectorAll(sel)) {{
                    const txt = el.textContent.trim();
                    const h = el.href || '';
                    if (txt.length > 10 && !seen.has(h) && (h.includes('readly.co') || h.includes('readly.com'))) {{
                        seen.add(h);
                        results.push(h);
                    }}
                }}
                if (results.length > index) break;
            }}
            return results[index] || '';
        }})({article_index})""")

        if not href:
            return {"error": f"Article at index {article_index} not found on this page"}

        await self.page.goto(href)
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        title = await self.page.title()
        text = await self.page.evaluate("""() => {
            const selectors = [
                '[class*="body"]', '[class*="content"]', '[class*="article"]',
                'article', 'main', '.reader-content', '[class*="text"]',
                '[class*="magazine"]', '[class*="reader"]'
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.textContent.length > 50) {
                    return el.textContent.trim();
                }
            }
            return document.body ? document.body.textContent.trim() : '';
        }""")

        author = await self.page.evaluate("""() => {
            const sel = document.querySelector(
                '[class*="author"], [class*="byline"], [class*="writer"], [rel="author"]'
            );
            return sel ? sel.textContent.trim() : '';
        }""")

        return {
            "title": title,
            "url": href,
            "author": author,
            "text": text[:20000] if text else "",
            "word_count": len(text.split()) if text else 0,
        }

    async def search_magazines(self, query: str) -> dict:
        """Navigate to Readly searching for magazines by keyword."""
        if not self.page:
            raise RuntimeError("Browser not started")

        domain = os.environ.get("READLY_DOMAIN", "www.readly.co")
        search_url = f"https://{domain}/search?q={query}"
        await self.page.goto(search_url)
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        results = await self.page.evaluate("""() => {
            const items = [];
            const selectors = [
                'a[href*="/magazine/"]',
                'a[href*="/catalogue/"]',
                '[class*="magazine"] a',
                '[class*="catalogue"] a',
                '[class*="search"] a[href*="readly"]'
            ];
            const seen = new Set();
            for (const sel of selectors) {
                for (const el of document.querySelectorAll(sel)) {
                    const txt = el.textContent.trim();
                    const href = el.href || '';
                    if (txt.length > 5 && !seen.has(href) && href !== window.location.href) {
                        seen.add(href);
                        items.push({
                            title: txt.substring(0, 200),
                            url: href,
                            type: href.includes('magazine') ? 'magazine' : 'catalogue'
                        });
                    }
                }
                if (items.length >= 5) break;
            }
            return items.slice(0, 20);
        }""")

        return {
            "query": query,
            "results": results,
            "count": len(results),
        }

    async def list_library(self) -> dict:
        """Scrape the Readly newsstand/magazine library page for all available issues."""
        if not self.page:
            raise RuntimeError("Browser not started")

        domain = os.environ.get("READLY_DOMAIN", "www.readly.co")
        token = os.environ.get("READLY_AUTH_TOKEN", "")
        newsstand_url = f"https://{domain}/at/newsstand"
        if token:
            newsstand_url = f"{newsstand_url}?readlyAuth={token}"
        await self.page.goto(newsstand_url)
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(3)
        # Scroll to trigger lazy loading
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.5)
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

        magazines = await self.page.evaluate("""() => {
            const results = [];
            const seen = new Set();

            // Strategy 1: Look for article/cover elements with magazine info
            const candidates = document.querySelectorAll(
                'a, article, [class*="tile"], [class*="card"], [class*="cover"], ' +
                '[class*="magazine"], [class*="issue"], [class*="publication"], ' +
                '[class*="item"], figure, [class*="grid"] > div'
            );

            for (const el of candidates) {
                const link = el.tagName === 'A' ? el : el.querySelector('a');
                const href = link ? (link.href || '') : '';
                const img = el.querySelector('img');
                const imgSrc = img ? (img.src || '') : '';
                const titleEl = el.querySelector(
                    '[class*="title"], [class*="name"], h1, h2, h3, h4, ' +
                    '[class*="heading"], figcaption, [class*="label"]'
                );
                const title = titleEl
                    ? titleEl.textContent.trim()
                    : (img ? img.alt || '' : el.textContent.trim());

                if (title && title.length > 3 && !seen.has(title)) {
                    seen.add(title);
                    results.push({
                        title: title.substring(0, 200),
                        url: href || window.location.href,
                        cover_url: imgSrc || '',
                        type: href.includes('/magazine/') ? 'magazine'
                            : href.includes('/issue/') ? 'issue'
                            : href.includes('/read/') ? 'article' : 'unknown',
                    });
                }
            }

            // Strategy 2: Fallback — grab all <img> with meaningful alt text
            if (results.length < 3) {
                for (const img of document.querySelectorAll('img[alt]')) {
                    const alt = img.alt.trim();
                    if (alt.length > 5 && !seen.has(alt)) {
                        seen.add(alt);
                        const parent = img.closest('a');
                        results.push({
                            title: alt.substring(0, 200),
                            url: parent ? parent.href : '',
                            cover_url: img.src || '',
                            type: 'magazine',
                        });
                    }
                }
            }

            return results.slice(0, 50);
        }""")

        return {
            "magazines": magazines,
            "count": len(magazines),
            "page_url": self.page.url,
        }

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
