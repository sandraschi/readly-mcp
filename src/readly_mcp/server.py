from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any
from urllib.request import urlopen, Request

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
    version="0.2.1",
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
        scraping_state["status"] = f"Error: {e!s}"
    finally:
        scraping_state["is_running"] = False


# --- MCP Tools ---


async def _ensure_browser() -> None:
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)


@mcp.tool()
async def open_readly_browser() -> str:
    """Opens the browser and navigates to Readly. Auto-logs in if READLY_AUTH_TOKEN env var is set.
    First run without the token will need manual login (persisted via user_data/ cookies)."""
    await browser_manager.start_browser(headless=False)
    await browser_manager.go_to_readly()
    has_token = bool(os.environ.get("READLY_AUTH_TOKEN", ""))
    return (
        "Browser opened and logged in via auth token."
        if has_token
        else "Browser opened. Please log in (cookies will be saved for next time)."
    )


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


@mcp.tool()
async def open_latest_issue(magazine_name: str) -> dict:
    """Search Readly and open the latest issue for a magazine by name."""
    await _ensure_browser()
    return await browser_manager.open_latest_issue(magazine_name)


@mcp.tool()
async def read_all_articles(max_articles: int = 10) -> dict:
    """Batch-extract full text for articles on the current issue page."""
    await _ensure_browser()
    return await browser_manager.read_all_articles(max_articles=max_articles)


@mcp.tool()
async def list_articles() -> dict:
    """Parse the current Readly magazine page and extract article titles + URLs.
    Requires the browser to be on a magazine issue page."""
    await _ensure_browser()
    return await browser_manager.list_articles()


@mcp.tool()
async def extract_article_text(article_index: int = 0) -> dict:
    """Extract the full text of an article from the current magazine issue by index.
    Call list_articles first to get available articles and their indices."""
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.extract_article_text(article_index)


@mcp.tool()
async def search_magazines(query: str) -> dict:
    """Search Readly for magazines matching a keyword query."""
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.search_magazines(query)


@mcp.tool()
async def list_library() -> dict:
    """Scrape the Readly newsstand for all available magazines/issues in your library."""
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.list_library()


# --- FastAPI API Bridge ---

_mcp_http = mcp.http_app(path="/mcp")

app = FastAPI(title="Readly MCP API", lifespan=_mcp_http.lifespan)
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
    return {"status": "healthy", "version": "0.2.1", "mcp_connected": True}


@app.get("/api/tools")
async def api_list_tools():
    tools = await mcp.list_tools()
    return [{"name": t.name, "description": t.description} for t in tools]


@app.post("/api/scrape/start")
async def api_start_scrape(issue_name: str, interval: int = 120, max_pages: int = 200):
    res = await smart_scrape(issue_name, interval, max_pages)
    if res.startswith("Error"):
        raise HTTPException(status_code=400, detail=res)
    return {"message": res}


@app.post("/api/scrape/stop")
async def api_stop_scrape():
    return {"message": stop_scrape()}


@app.get("/api/magazines/latest")
async def api_open_latest(name: str = ""):
    if not name.strip():
        raise HTTPException(status_code=400, detail="name parameter required")
    await _ensure_browser()
    return await browser_manager.open_latest_issue(name)


@app.get("/api/articles/read-all")
async def api_read_all_articles(max: int = 10):
    await _ensure_browser()
    return await browser_manager.read_all_articles(max_articles=max)


@app.get("/api/articles/list")
async def api_list_articles():
    await _ensure_browser()
    return await browser_manager.list_articles()


@app.get("/api/articles/extract")
async def api_extract_article(index: int = 0):
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.extract_article_text(index)


@app.get("/api/magazines/search")
async def api_search_magazines(q: str = ""):
    if not q:
        raise HTTPException(status_code=400, detail="q parameter is required")
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.search_magazines(q)


@app.get("/api/library")
async def api_list_library():
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.list_library()


@app.get("/api/magazines/open")
async def api_open_magazine(url: str = ""):
    if not url:
        raise HTTPException(status_code=400, detail="url parameter is required")
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.open_url(url)


@app.post("/api/content/match")
async def api_content_match(body: dict):
    """Search watch-list magazines on Readly for articles matching a query (e.g. arXiv paper title)."""
    query = str(body.get("query") or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    magazines = body.get("magazines")
    if magazines is not None and not isinstance(magazines, list):
        raise HTTPException(status_code=400, detail="magazines must be a list")
    try:
        await browser_manager.start_browser(headless=False)
    except Exception as exc:
        logger.debug("Browser already running: %s", exc)
    return await browser_manager.match_magazine_articles(
        query,
        magazines,
        max_per_magazine=int(body.get("max_per_magazine") or 3),
    )


@app.get("/api/pipeline/liveness")
async def api_pipeline_liveness():
    """Fleet probe: auth token, browser, scrape job state."""
    from readly_mcp.core.browser import get_last_poll_stats

    token = bool(os.environ.get("READLY_AUTH_TOKEN", "").strip())
    browser_up = browser_manager.page is not None
    alerts: list[dict] = []
    if not token:
        alerts.append(
            {
                "severity": "warning",
                "code": "READLY_AUTH_TOKEN_MISSING",
                "message": "READLY_AUTH_TOKEN not set — login may fail",
            }
        )
    if scraping_state.get("is_running"):
        alerts.append(
            {
                "severity": "info",
                "code": "READLY_SCRAPE_ACTIVE",
                "message": f"Scrape running: {scraping_state.get('issue_name')}",
            }
        )
    last_poll = get_last_poll_stats()
    return {
        "success": True,
        "healthy": True,
        "service": "readly-mcp",
        "version": "0.2.1",
        "auth_token_set": token,
        "browser_active": browser_up,
        "scrape_status": scraping_state.get("status"),
        "last_poll": last_poll,
        "alerts": alerts,
    }


@app.post("/api/auth/token")
async def api_set_auth_token(token: str = ""):
    """Set the Readly auth token (stored in env, not persisted to disk)."""
    if token:
        os.environ["READLY_AUTH_TOKEN"] = token
        return {"ok": True, "message": "Auth token set for this session"}
    return {"ok": False, "message": "No token provided"}


@app.post("/api/settings")
async def api_update_settings(body: dict):
    """Update runtime settings (stored in env for current session)."""
    if body.get("auth_token"):
        os.environ["READLY_AUTH_TOKEN"] = body["auth_token"]
    if body.get("scrape_interval"):
        os.environ["READLY_SCRAPE_INTERVAL"] = str(body["scrape_interval"])
    if body.get("max_pages"):
        os.environ["READLY_MAX_PAGES"] = str(body["max_pages"])
    return {"ok": True, "message": "Settings saved for this session"}


# --- LLM Endpoints ---


@app.get("/api/settings")
async def api_get_settings():
    """Return current LLM settings."""
    return {
        "ollama_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.environ.get("OLLAMA_MODEL", ""),
        "lmstudio_url": os.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1"),
        "lmstudio_model": os.environ.get("LMSTUDIO_MODEL", ""),
        "provider": os.environ.get("LLM_PROVIDER", "ollama"),
        "local_llm_url": os.environ.get("LOCAL_LLM_URL", ""),
        "local_llm_key": os.environ.get("LOCAL_LLM_KEY", ""),
    }


@app.post("/api/settings/llm")
async def api_update_llm_settings(body: dict):
    """Update LLM provider settings for the session."""
    if body.get("ollama_url"):
        os.environ["OLLAMA_URL"] = body["ollama_url"]
    if body.get("ollama_model"):
        os.environ["OLLAMA_MODEL"] = body["ollama_model"]
    if body.get("lmstudio_url"):
        os.environ["LMSTUDIO_URL"] = body["lmstudio_url"]
    if body.get("lmstudio_model"):
        os.environ["LMSTUDIO_MODEL"] = body["lmstudio_model"]
    if body.get("provider"):
        os.environ["LLM_PROVIDER"] = body["provider"]
    if body.get("local_llm_url"):
        os.environ["LOCAL_LLM_URL"] = body["local_llm_url"]
    if body.get("local_llm_key"):
        os.environ["LOCAL_LLM_KEY"] = body["local_llm_key"]
    return {"ok": True, "message": "LLM settings saved for this session"}


@app.get("/api/llm/models")
async def api_list_llm_models(provider: str = "ollama"):
    """List available models from the configured LLM provider."""
    if provider == "ollama":
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        try:
            req = Request(f"{url}/api/tags", method="GET")
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            return {"ok": True, "provider": "ollama", "models": models}
        except Exception as e:
            return {"ok": False, "provider": "ollama", "error": str(e), "models": []}
    elif provider == "lmstudio":
        url = os.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1")
        try:
            req = Request(f"{url}/models", method="GET",
                          headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            models = [m["id"] for m in data.get("data", [])]
            return {"ok": True, "provider": "lmstudio", "models": models}
        except Exception as e:
            return {"ok": False, "provider": "lmstudio", "error": str(e), "models": []}
    return {"ok": False, "provider": provider, "error": "Unknown provider", "models": []}


@app.post("/api/llm/chat")
async def api_llm_chat(body: dict):
    """Send a chat message to the configured LLM."""
    provider = body.get("provider", os.environ.get("LLM_PROVIDER", "ollama"))
    message = body.get("message", "")
    if not message:
        return {"ok": False, "error": "No message provided"}

    if provider == "ollama":
        model = body.get("model", os.environ.get("OLLAMA_MODEL", "qwen3.5:27b"))
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }).encode()
        try:
            req = Request(f"{url}/api/chat", data=payload,
                          headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            return {"ok": True, "response": data.get("message", {}).get("content", "")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    elif provider == "lmstudio":
        model = body.get("model", os.environ.get("LMSTUDIO_MODEL", ""))
        url = os.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1")
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 1024,
        }).encode()
        try:
            req = Request(f"{url}/chat/completions", data=payload,
                          headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            return {"ok": True, "response": data.get("choices", [{}])[0].get("message", {}).get("content", "")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    elif provider == "openai":
        model = body.get("model", os.environ.get("LOCAL_LLM_MODEL", "gpt-4o-mini"))
        url = body.get("base_url", os.environ.get("LOCAL_LLM_URL", ""))
        api_key = body.get("api_key", os.environ.get("LOCAL_LLM_KEY", ""))
        if not url:
            return {"ok": False, "error": "No OpenAI-compatible URL configured"}
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 1024,
        }).encode()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            req = Request(f"{url}/chat/completions", data=payload, headers=headers)
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            return {"ok": True, "response": data.get("choices", [{}])[0].get("message", {}).get("content", "")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    return {"ok": False, "error": f"Unknown provider: {provider}"}


@app.get("/api/llm/status")
async def api_llm_status():
    """Check connectivity to the configured LLM provider."""
    provider = os.environ.get("LLM_PROVIDER", "ollama")
    result = {"provider": provider, "ok": False, "error": None, "model": None}

    if provider == "ollama":
        url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        model = os.environ.get("OLLAMA_MODEL", "")
        try:
            req = Request(f"{url}/api/tags", method="GET")
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            result["ok"] = True
            result["model"] = model if model in models else (models[0] if models else None)
            result["available_models"] = models
        except Exception as e:
            result["error"] = str(e)

    elif provider == "lmstudio":
        url = os.environ.get("LMSTUDIO_URL", "http://localhost:1234/v1")
        model = os.environ.get("LMSTUDIO_MODEL", "")
        try:
            req = Request(f"{url}/models", method="GET",
                          headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            models = [m["id"] for m in data.get("data", [])]
            result["ok"] = True
            result["model"] = model if model in models else (models[0] if models else None)
            result["available_models"] = models
        except Exception as e:
            result["error"] = str(e)

    return result


# Mount MCP HTTP transport alongside the REST bridge
app.mount("/mcp", _mcp_http)


def main():
    import threading

    from .transport import run_server

    # Start HTTP bridge in background for REST API + MCP HTTP, then run stdio
    web_port = int(os.getenv("WEB_PORT", "10863"))
    http_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="127.0.0.1", port=web_port, log_level="warning"),
        daemon=True,
    )
    http_thread.start()
    logger.info("HTTP bridge running on port %d", web_port)
    run_server(mcp, server_name="readly-mcp")




if __name__ == "__main__":
    main()
