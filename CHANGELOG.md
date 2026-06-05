# Changelog

All notable changes to **readly-mcp** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.1] — 2026-06-05

### Added
- **Article list quality gate** — `_quality_check_articles()` rejects nav/header scrape noise (`Home`, `My Library`, …); `extraction_failed` + `reason` in `list_articles` responses.
- **`GET /api/pipeline/liveness`** — poll stats (`articles_extracted`, `low_yield_magazines`, `last_run_at`) for `fleet-agent-mcp` pipeline probes.
- **`record_poll_stats` / `get_last_poll_stats`** — browser manager telemetry for fleet health cards.
- **Tests** — `tests/unit/test_browser_quality.py` for TOC vs nav detection.
- **`AGENTS.md`** — agent install context for the repo.

### Fleet integration (intel lane)
- **arxiv-mcp** — `readly_client` calls `/api/content/match` for magazine full-text (see arxiv `docs/READLY_INTEGRATION.md`).
- **aiwatcher-mcp** — `READLY_ENABLED` poll ingests `feed_type=readly` items; Fritz `intel_briefing` applies longform relevance threshold.
- **Unblocks** prior aiwatcher PRD deferral: article pipeline no longer blocked on missing `list_current_issue_articles` — `list_articles` + watchlist mode is the supported path.

### Changed
- **`web_sota/vite.config.ts`** — frontend port **10846** (fleet registry alignment).
- **Browser** — expanded nav title blocklist; improved magazine/article discovery selectors.

### Documentation
- Cross-referenced from `arxiv-mcp/docs/READLY_INTEGRATION.md` and `mcp-central-docs` fleet intel lane notes.

## [0.2.0] — 2026-04-21

### Added
- FastMCP 3.2 server with Playwright scrape loop, PDF export, dual transport.
- `web_sota` dashboard; ports **10863** / **10864** (backend / frontend per WEBAPP_PORTS).
