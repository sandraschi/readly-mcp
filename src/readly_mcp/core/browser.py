import asyncio
import logging
import os
from datetime import UTC, datetime

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

log = logging.getLogger(__name__)

_NAV_TITLE_BLOCKLIST = frozenset({
    "home", "my library", "search", "discover", "categories", "newsstand",
    "settings", "account", "sign in", "log in", "readly", "back", "menu",
    "magazines", "newspapers", "podcasts",
})

_last_poll_stats: dict = {
    "magazines_attempted": 0,
    "articles_extracted": 0,
    "avg_word_count": 0,
    "low_yield_magazines": [],
    "last_run_at": None,
    "magazine": None,
}


def record_poll_stats(**kwargs) -> None:
    global _last_poll_stats
    _last_poll_stats.update(kwargs)
    _last_poll_stats["last_run_at"] = datetime.now(UTC).isoformat()
    if kwargs.get("articles_extracted", 0) < 2:
        mag = kwargs.get("magazine")
        if mag:
            lows = list(_last_poll_stats.get("low_yield_magazines") or [])
            if mag not in lows:
                lows.append(mag)
            _last_poll_stats["low_yield_magazines"] = lows[-10:]


def get_last_poll_stats() -> dict:
    return dict(_last_poll_stats)


def _quality_check_articles(raw: list[dict]) -> dict:
    """Reject listings that look like nav/header scrape, not issue TOC."""
    cleaned: list[dict] = []
    for row in raw:
        title = (row.get("title") or "").strip()
        href = (row.get("url") or "").strip()
        if len(title) < 12:
            continue
        if title.lower() in _NAV_TITLE_BLOCKLIST:
            continue
        if not href and len(title) < 20:
            continue
        cleaned.append({"title": title[:200], "url": href})

    if not cleaned:
        return {"articles": [], "extraction_failed": True, "reason": "no_articles_after_filter"}

    nav_hits = sum(
        1 for a in raw if (a.get("title") or "").strip().lower() in _NAV_TITLE_BLOCKLIST
    )
    if nav_hits >= 2 and nav_hits >= max(1, len(raw) // 2):
        return {"articles": [], "extraction_failed": True, "reason": "nav_elements_detected"}

    if cleaned[0]["title"].lower() in _NAV_TITLE_BLOCKLIST:
        return {"articles": [], "extraction_failed": True, "reason": "nav_elements_detected"}

    return {"articles": cleaned, "extraction_failed": False}

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

    async def _scroll_lazy_issue_index(self) -> None:
        """Scroll issue index to trigger lazy-loaded article cards."""
        prev_count = 0
        for _ in range(5):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.0)
            count = await self.page.evaluate(
                """() => document.querySelectorAll('a[href*="/read/"]').length"""
            )
            if count == prev_count:
                break
            prev_count = count
        await self.page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

    async def list_articles(self) -> dict:
        """Parse the current Readly magazine page DOM to extract article titles and URLs."""
        if not self.page:
            raise RuntimeError("Browser not started")

        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(1.5)
        await self._scroll_lazy_issue_index()

        page_title = await self.page.title()
        page_url = self.page.url

        articles = await self.page.evaluate("""() => {
            const results = [];
            const seen = new Set();
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
            }
            if (results.length === 0) {
                for (const h of document.querySelectorAll('h1,h2,h3,h4')) {
                    const text = h.textContent.trim();
                    if (text.length > 10) results.push({title: text, url: ''});
                }
            }
            return results;
        }""")

        checked = _quality_check_articles(articles)
        if checked.get("extraction_failed"):
            log.warning(
                "list_articles quality check failed: %s (url=%s)",
                checked.get("reason"),
                page_url,
            )
            return {
                "issue_title": page_title,
                "page_url": page_url,
                "articles": [],
                "count": 0,
                "extraction_failed": True,
                "reason": checked.get("reason"),
            }

        cleaned = checked["articles"]
        return {
            "issue_title": page_title,
            "page_url": page_url,
            "articles": [
                {"title": a["title"], "url": a["url"], "index": i}
                for i, a in enumerate(cleaned)
            ],
            "count": len(cleaned),
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

    async def open_url(self, url: str) -> dict:
        """Navigate browser to a Readly magazine/issue URL."""
        if not self.page:
            raise RuntimeError("Browser not started")
        if not url.strip().startswith("http"):
            return {"success": False, "error": "invalid_url"}
        await self.page.goto(url.strip())
        await self.page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)
        return {"success": True, "url": self.page.url, "title": await self.page.title()}

    async def open_latest_issue(self, magazine_name: str) -> dict:
        """Search for magazine_name and open the best catalogue/issue result."""
        if not self.page:
            raise RuntimeError("Browser not started")

        name = (magazine_name or "").strip()
        if not name:
            return {"success": False, "error": "magazine_name required"}

        search = await self.search_magazines(name)
        results = search.get("results") or []
        if not results:
            return {
                "success": False,
                "error": f"Magazine not found: {name}",
                "query": name,
                "results_count": 0,
            }

        pick = results[0]
        for candidate in results[:5]:
            url = candidate.get("url") or ""
            if "/read/" in url or "/issue/" in url or "catalogue" in url:
                pick = candidate
                break

        opened = await self.open_url(pick.get("url") or "")
        if not opened.get("success"):
            return opened

        return {
            "success": True,
            "magazine_name": name,
            "magazine_title": pick.get("title"),
            "url": opened.get("url"),
            "title": opened.get("title"),
            "issue_title": opened.get("title"),
        }

    async def read_all_articles(self, max_articles: int = 10) -> dict:
        """Extract full text for articles on the current issue page."""
        if not self.page:
            raise RuntimeError("Browser not started")

        issue_url = self.page.url
        listing = await self.list_articles()
        if listing.get("extraction_failed"):
            return {
                "success": False,
                "issue_url": issue_url,
                "error": listing.get("reason", "list_articles failed"),
                "articles": [],
                "count": 0,
            }

        cap = max(1, int(max_articles))
        articles_meta = (listing.get("articles") or [])[:cap]
        results: list[dict] = []
        skipped: list[dict] = []

        for i, meta in enumerate(articles_meta):
            if self.page.url != issue_url:
                await self.page.goto(issue_url)
                await self.page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(1.5)
                listing = await self.list_articles()
                if listing.get("extraction_failed"):
                    break
                articles_meta = listing.get("articles") or []
                if i >= len(articles_meta):
                    break
                meta = articles_meta[i]

            extracted = await self.extract_article_text(int(meta.get("index", i)))
            if extracted.get("error"):
                skipped.append({
                    "index": meta.get("index"),
                    "title": meta.get("title"),
                    "error": extracted["error"],
                })
                continue
            if extracted.get("word_count", 0) < 50:
                skipped.append({
                    "index": meta.get("index"),
                    "title": meta.get("title"),
                    "error": "low_word_count",
                })
                continue
            results.append(extracted)

        avg_wc = (
            sum(a.get("word_count", 0) for a in results) / len(results) if results else 0
        )
        record_poll_stats(
            magazines_attempted=1,
            articles_extracted=len(results),
            avg_word_count=int(avg_wc),
            magazine=listing.get("issue_title"),
        )

        return {
            "success": len(results) > 0,
            "issue_title": listing.get("issue_title"),
            "issue_url": issue_url,
            "articles": results,
            "count": len(results),
            "skipped": skipped,
            "avg_word_count": int(avg_wc),
        }

    async def match_magazine_articles(
        self,
        query: str,
        magazine_names: list[str] | None = None,
        *,
        max_per_magazine: int = 3,
    ) -> dict:
        """Search Readly magazines and list articles whose titles overlap the query."""
        import re

        if not self.page:
            await self.start_browser(headless=False)

        names = [n.strip() for n in (magazine_names or []) if n and n.strip()]
        if not names:
            names = ["New Scientist"]

        query_words = [
            w.lower()
            for w in re.findall(r"[a-z0-9]{4,}", query.lower())
            if w not in ("with", "from", "using", "paper", "that", "this")
        ][:8]
        hits: list[dict] = []

        for mag_name in names:
            search = await self.search_magazines(mag_name)
            results = search.get("results") or []
            if not results:
                continue
            opened = await self.open_url(results[0].get("url") or "")
            if not opened.get("success"):
                continue
            listing = await self.list_articles()
            for article in listing.get("articles") or []:
                title = str(article.get("title") or "")
                blob = title.lower()
                score = sum(1 for w in query_words if w in blob)
                if score >= 2 or (len(query_words) == 1 and query_words[0] in blob):
                    hits.append(
                        {
                            "magazine": mag_name,
                            "title": title,
                            "url": article.get("url"),
                            "index": article.get("index"),
                            "issue_title": listing.get("issue_title"),
                            "match_score": score,
                        }
                    )
            if len([h for h in hits if h.get("magazine") == mag_name]) >= max_per_magazine:
                continue

        hits.sort(key=lambda h: int(h.get("match_score") or 0), reverse=True)
        return {
            "query": query,
            "magazines_searched": names,
            "hits": hits[:15],
            "count": len(hits[:15]),
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
