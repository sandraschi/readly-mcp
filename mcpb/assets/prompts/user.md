# readly-mcp — User Guide

## Quick Start

readly-mcp enables automated access to Readly digital magazines through browser automation. To get started:

1. Set READLY_AUTH_TOKEN if you have an existing Readly session token
2. Start the server (default: stdio for MCP, HTTP bridge on port 11201)
3. Open the browser: open_readly_browser()
4. If no token is set, log in manually in the opened browser (cookies saved)
5. Start exploring magazines, scraping issues, and extracting articles

**First commands:**
```
open_readly_browser()
list_library()
search_magazines(query="technology")
open_latest_issue(magazine_name="The Economist")
```

## Tutorials

### Tutorial 1: First Readly Session

Get connected to Readly and explore the library.

**Steps:**
1. Launch the browser and navigate to Readly:
   `open_readly_browser()`

2. If prompted, log in to your Readly account in the browser window

3. Browse your library:
   `list_library()`

4. Search for a magazine topic:
   `search_magazines(query="science")`

**Expected outcome:** Browser opens at Readly with full library access.

### Tutorial 2: Scraping a Magazine Issue

Automatically capture and save a complete magazine issue as PDF.

**Steps:**
1. Open the target magazine:
   `open_latest_issue(magazine_name="The Economist")`

2. Start the automated scrape:
   `smart_scrape(issue_name="The Economist - March 2026", interval_seconds=120, max_pages=200)`

3. Monitor progress:
   `get_status()`

4. Wait for completion (status changes to "Completed")

5. Find the PDF at ~/Desktop/readly/The_Economist_-_March_2026_full.pdf

**Expected outcome:** Complete magazine issue saved as PDF to desktop.

### Tutorial 3: Article Extraction

Extract readable text content from magazine articles.

**Steps:**
1. Open a magazine issue:
   `open_latest_issue(magazine_name="National Geographic")`

2. List available articles:
   `list_articles()`

3. Extract a specific article:
   `extract_article_text(article_index=0)`

4. Extract all articles:
   `read_all_articles(max_articles=10)`

**Expected outcome:** Structured article text with titles and content.

### Tutorial 4: Magazine Discovery and Search

Find magazines matching your interests.

**Steps:**
1. Search by broad topic:
   `search_magazines(query="cooking")`

2. Search for specific title:
   `search_magazines(query="economist")`

3. Browse full library:
   `list_library()`

4. Open a discovered magazine:
   `open_latest_issue(magazine_name="BBC Science Focus")`

**Expected outcome:** Discovered magazines ready for reading or scraping.

### Tutorial 5: Content Matching for Research

Search watch-list magazines for specific content matching research topics.

**Steps:**
1. Configure your watch-list magazines (in READLY_WATCHLIST env var)

2. Match content against a query:
   `api_content_match(magazines=["The Economist", "New Scientist"], query="artificial intelligence", max_per_magazine=3)`

3. Review matched articles and their relevance

**Expected outcome:** Relevant articles from your subscribed magazines matched to your research query.

### Tutorial 6: Pipeline Health Monitoring

Monitor the readly-mcp pipeline for fleet operations.

**Steps:**
1. Check pipeline liveness:
   `api_pipeline_liveness()`

2. Verify system health:
   `api_health()`

3. Check current scrape status:
   `api_get_status()`

**Expected outcome:** Full visibility into pipeline health and operation status.

### Tutorial 7: LLM Integration Setup

Configure local LLM providers for AI-powered features.

**Steps:**
1. Check current settings:
   `api_get_settings()`

2. Discover available providers:
   `api_llm_providers()`

3. Set active provider:
   `api_update_llm_settings(body={"provider": "ollama", "ollama_model": "llama3.2"})`

4. Verify connectivity:
   `api_llm_status()`

5. Test with a chat message:
   `api_llm_chat(body={"message": "Summarize the benefits of digital magazines"})`

**Expected outcome:** Local LLM configured and responding.

### Tutorial 8: Magazine Research Workflow

Complete research workflow from discovery to content extraction.

**Steps:**
1. Discover magazines in your field:
   `search_magazines(query="artificial intelligence")`

2. Open the most relevant issue:
   `open_latest_issue(magazine_name="Wired UK")`

3. List articles in the issue:
   `list_articles()`

4. Extract the most relevant articles:
   `extract_article_text(article_index=0)`
   `extract_article_text(article_index=1)`

5. Save the complete issue for offline reference:
   `smart_scrape(issue_name="Wired UK - Latest", interval_seconds=90, max_pages=150)`

**Expected outcome:** Complete research package with article text and full issue PDF.

### Tutorial 9: Settings and Token Management

Manage authentication and runtime configuration.

**Steps:**
1. Set auth token for session:
   `api_set_auth_token(token="your-readly-token")`

2. Update scrape settings:
   `api_update_settings(body={"scrape_interval": 60, "max_pages": 100})`

3. Configure LLM:
   `api_update_llm_settings(body={"provider": "lmstudio", "lmstudio_model": "qwen3.5-27b"})`

4. Verify all settings:
   `api_get_settings()`

**Expected outcome:** Fully configured server with persistent settings.

### Tutorial 10: Batch Article Processing

Process multiple articles from an issue systematically.

**Steps:**
1. Open the magazine:
   `open_latest_issue(magazine_name="New Scientist")`

2. Get all articles:
   `list_articles()`

3. Extract first batch:
   `read_all_articles(max_articles=5)`

4. Extract additional articles individually:
   `extract_article_text(article_index=5)`
   `extract_article_text(article_index=6)`

5. Check scrape status after processing:
   `get_status()`

**Expected outcome:** All articles from the issue extracted and accessible.

## API Reference

### REST Endpoints

The server exposes HTTP endpoints on the configured WEB_PORT (default 11201):

**System Endpoints:**
- GET /api/health: Health check
- GET /api/status: Scrape status
- GET /api/tools: List MCP tools
- GET /api/pipeline/liveness: Fleet health probe

**Scraping Endpoints:**
- POST /api/scrape/start: Start scrape (params: issue_name, interval, max_pages)
- POST /api/scrape/stop: Stop scraping

**Magazine Endpoints:**
- GET /api/magazines/latest: Open latest issue (param: name)
- GET /api/magazines/search: Search magazines (param: q)
- GET /api/magazines/open: Open by URL (param: url)

**Article Endpoints:**
- GET /api/articles/list: List articles
- GET /api/articles/read-all: Read all articles (param: max)
- GET /api/articles/extract: Extract article (param: index)

**Library Endpoints:**
- GET /api/library: List library

**Content Endpoints:**
- POST /api/content/match: Content matching (body: query, magazines, max_per_magazine)

**Auth Endpoints:**
- POST /api/auth/token: Set auth token (param: token)

**Settings Endpoints:**
- POST /api/settings: Update settings
- GET /api/settings: Get settings
- POST /api/settings/llm: Update LLM settings

**LLM Endpoints:**
- GET /api/llm/models: List models (param: provider)
- POST /api/llm/chat: Chat with LLM (body: message, model, provider)
- GET /api/llm/providers: Discover providers
- GET /api/llm/status: Check LLM status

## Troubleshooting

### Browser Issues

**Problem: Browser fails to launch**
Ensure Playwright is installed: pip install playwright && playwright install chromium. Check system has a display/GUI.

**Problem: Readly login fails**
Verify READLY_AUTH_TOKEN is correct. Delete user_data directory and try manual login.

**Problem: Browser times out on page load**
Check internet connection. Readly may be slow for large issues.

### Scraping Issues

**Problem: Scraping detects end too early**
The duplicate page detection may trigger on long-loading pages. Restart scrape.

**Problem: PDF compilation fails**
Ensure ~/Desktop/readly directory exists. Check disk space for large magazines.

**Problem: Scraping gets stuck on a page**
Use stop_scrape() and restart with a longer interval_seconds.

### LLM Issues

**Problem: LLM provider not found**
Verify the provider is running. Check OLLAMA_URL or LMSTUDIO_URL configuration.

**Problem: Chat returns empty response**
Check the model name. Try api_llm_providers() to see available models.

## FAQ

**Q: Do I need a Readly subscription?**
A: Yes. Readly is a subscription-based digital magazine service. You need a valid account.

**Q: How does authentication work?**
A: Set READLY_AUTH_TOKEN for auto-login, or log in manually in the browser window. Cookies persist.

**Q: Where are PDFs saved?**
A: PDFs are saved to ~/Desktop/readly/ on Windows.

**Q: Can I scrape multiple magazines at once?**
A: Only one scrape job runs at a time. Queue magazines sequentially.

**Q: What determines scrape speed?**
A: The interval_seconds parameter controls time between page turns. Default is 120 seconds.

**Q: Does the server work on Linux?**
A: Playwright works on Linux, but the browser will need headless mode configuration.

**Q: Can I use OpenAI instead of local LLMs?**
A: Yes. Set LOCAL_LLM_URL and LOCAL_LLM_KEY for OpenAI-compatible endpoints.

## Browser Cookie Management

The Playwright browser persists authentication cookies in the user_data directory, allowing sessions to survive server restarts. The cookie file is stored alongside the server and is automatically created on first browser launch. If you encounter authentication errors, the session may have expired. Use open_readly_browser() to attempt re-authentication. If that fails, delete the user_data directory to force a fresh login prompt. Cookies are stored in Chrome's standard format and are specific to the Readly domain.

## PDF Output Customization

By default, compiled PDFs are saved to ~/Desktop/readly/ with the issue name as filename. Each screenshot is placed on a separate PDF page at full page size. The PDF uses A4 page dimensions by default with the screenshot scaled to fit. The output quality matches the screenshot resolution captured from the browser. For higher quality PDFs, ensure the browser window is set to a high resolution before starting the scrape.

## Magazine Discovery Tips

For effective magazine discovery, use specific search terms rather than broad categories. Searching for "science" returns general science magazines, while "marine biology" returns more specialized publications. Use the list_library tool to browse all available magazines after logging in, which provides a complete catalog. Bookmark favorite magazines by noting their exact names for use with open_latest_issue. The search results include issue frequency information to help identify weekly versus monthly publications for planning scrape schedules.

## Authentication Troubleshooting

If the Readly auth token is not working, first verify the token is correctly copied from your Readly browser session. Auth tokens expire periodically and may need to be refreshed from a new browser session. Use api_set_auth_token to update the token without restarting the server. If using manual login instead of token authentication, ensure you complete the login within the browser window before the session times out. For persistent authentication issues, verify your Readly subscription is active and your account is in good standing.

## Scraping Large Issues

When scraping large magazine issues with 150+ pages, configure parameters for reliability. Set interval_seconds between 150-180 seconds to ensure each page fully loads before capture. Set max_pages to 250 or higher to accommodate oversized issues. Monitor progress with get_status periodically. If the scraping appears stuck, the duplicate page detection may have triggered prematurely; check the status message and consider restarting with a larger interval. Large issues may require 6-12 hours to complete with conservative timing, so plan accordingly.

## Article Text Quality

The quality of extracted article text depends on how Readly renders the article content in the browser. Articles with clear text layout extract cleanly with proper paragraph structure. Articles with complex layouts, multiple columns, or embedded media may extract with formatting artifacts. The extract_article_text tool returns the best available text content from the article page. For critical research use, verify extracted text against the visual page content.

## Scheduled Scraping Strategy

For regular magazine reading or research workflows, establish a consistent scraping schedule. Set up weekly scraping for weekly publications like The Economist and New Scientist using consistent issue naming conventions. Use the same interval_seconds settings for comparable magazines to get predictable completion times. Monitor completion status and adjust intervals if pages are consistently missed. Archive completed PDFs to a permanent storage location for long-term reference. Use descriptive issue names including dates for easy identification in the output directory.

## Content Organization Tips

Organize your scraped magazine content for efficient retrieval. Use consistent naming conventions for issue_name parameters that include the magazine title, publication date, and edition. Create a folder structure on disk to organize PDFs by magazine title and year. Tag extracted articles with topic keywords using external tools. Build a research database from extracted article text for long-term reference. The content matching feature helps find relevant articles across your magazine collection when searching by topic.

## Magazine State Persistence

The browser session maintains magazine state between operations. After opening a magazine with open_latest_issue, the session stays on that magazine's reader page until another navigation command is issued. The list_articles operation reads from the currently loaded page. The extract_article_text and read_all_articles operations operate on the current magazine context. To switch magazines, use open_latest_issue again with a different magazine name. The get_status operation reports which magazine is currently loaded.

## Troubleshooting Common Browser Issues

If the browser window appears but does not navigate to Readly, verify the internet connection and check if Readly is accessible from a regular browser. If the browser opens but Readly shows a login page despite having READLY_AUTH_TOKEN configured, the token may have expired. Generate a new token and set it with api_set_auth_token. If the browser crashes during a long scrape, the scraping state is preserved in memory but the browser needs to be restarted with open_readly_browser. If pages are not loading correctly, the browser may have encountered a memory issue; restart the browser and resume scraping.

## Working with Large Libraries

When your Readly library has many magazines, finding specific issues requires efficient search strategies. Use search_magazines with specific keywords rather than browsing the entire library. Remember magazine names for direct access with open_latest_issue. Use content matching for topic-based discovery across your watch list. Organize your scraping by priority, starting with time-sensitive issues like weekly publications. Archive scraped magazines to free up mental space for new content discovery.

## Tutorial 13: Research Paper to Magazine Article Matching

Use readly-mcp to find magazine coverage of academic research papers.

**Steps:**
1. Prepare a list of recent arXiv paper titles in your research field
2. Set up your watch-list magazines in the READLY_WATCHLIST environment variable
3. For each paper title, use content matching: api_content_match(query="paper title here", magazines=["The Economist", "New Scientist"])
4. Review matched articles for popular science coverage of the research
5. Open matched articles directly with open_latest_issue and extract article text
6. Compile matched articles with the original paper for a complete research package

## Tutorial 14: Magazine Watchlist Management

Set up and manage a watch list of magazines for regular content monitoring.

**Steps:**
1. Identify magazines relevant to your research or interests using search_magazines
2. Set READLY_WATCHLIST environment variable with comma-separated magazine names
3. Use api_pipeline_liveness to verify the watch list is configured
4. Periodically run content matching: api_content_match(query="your research topic")
5. Review matched articles and extract relevant content
6. Update the watch list as your research interests evolve
7. Archive relevant articles for long-term reference

## Using Multiple LLM Providers

The server supports switching between LLM providers for different use cases. Use Ollama for quick, local responses with models like llama3.2 or gemma. Use LM Studio for more powerful local models like qwen3.5 or deepseek-coder. Use OpenAI-compatible endpoints for cloud-based models like GPT-4o. Switch providers based on task requirements: local for privacy-sensitive queries, cloud for complex analysis. The api_update_llm_settings endpoint allows provider switching without restarting the server.

## Troubleshooting Browser Persistence

If the browser behavior becomes unreliable after extended use, the accumulated state may need resetting. Use stop_scrape to end any active operations. Close the browser window manually if it becomes unresponsive. Restart the browser with open_readly_browser. If issues persist, the user_data directory may have become corrupted; delete it and restart the browser for a fresh session. Regular browser restarts between large scraping sessions help maintain reliability.

## Pipeline Liveness Monitoring

The api_pipeline_liveness endpoint provides comprehensive health monitoring for fleet integration. It reports whether the READLY_AUTH_TOKEN is configured, whether the browser is actively connected, the current scrape job status, last poll statistics showing recent activity, and any active alerts. Use this endpoint as a health check in monitoring systems. Set up alerts for missing auth tokens or stuck scrape jobs. The endpoint returns structured JSON for easy integration with fleet monitoring.

## Tutorial 15: Automated Research Pipeline

Set up a research pipeline that automatically monitors magazine content for topics of interest.

**Steps:**
1. Define your research topics and keywords
2. Set up watch-list magazines covering each topic area
3. Configure READLY_WATCHLIST with relevant magazine names
4. Periodically run content matching: api_content_match(query="research keyword", magazines=["Relevant Magazines"])
5. Extract matched articles for reading and analysis
6. Archive findings with the original publication metadata
7. Review and refine your watch list based on content quality and relevance

## Managing Multiple Watch Lists

For comprehensive research coverage, organize multiple watch lists by topic area. Create separate watch lists for technology, science, business, and other research domains using environment variable configuration. Each watch list can contain 5-10 magazines for focused monitoring. Rotate watch lists weekly to cover different research areas. Use content matching with topic-specific queries against the relevant watch list. Periodically review and update watch lists based on magazine content quality. Remove magazines that no longer provide relevant content for your research needs.

## Magazine Content Freshness

Magazine issues are published on regular schedules. Weekly magazines typically publish new issues every 7 days. Monthly magazines publish every 30 days. The open_latest_issue tool always retrieves the most recent issue available in your Readly subscription. Content matching results reflect the latest available issues from your watch list magazines. For time-sensitive research, scrape new issues promptly after publication. Archived PDFs capture the magazine content at the time of scraping for permanent reference.

## Session Management Best Practices

The browser session persists across operations to maintain magazine context. The session remains active until the server restarts or the browser crashes. For long-running server instances, periodically restart the browser to clear accumulated memory. Use open_readly_browser to reinitialize the browser if operations become sluggish. The browser session is tied to the server process; restarting the server starts a fresh session requiring re-authentication if cookies are not persisted.

## API Rate Limiting

The server's LLM API endpoints implement rate limiting to prevent overwhelming local providers. The api_llm_chat endpoint enforces a maximum request rate for chat completions. The api_list_llm_models endpoint can be called more frequently for provider discovery. For batch LLM operations, space out requests with appropriate delays. The server uses non-streaming requests to simplify response handling. Rate limits are not enforced on the scraping operations since they use their own configurable delay mechanisms.

## Scraping Schedule Planning

Plan your scraping schedule based on magazine publication frequency. Weekly magazines should be scraped soon after publication for timely content. Monthly magazines can be scraped at the beginning of each month. Quarterly magazines need less frequent attention. Balance scraping frequency against the time required for each scrape. Consider scraping multiple magazines in a batch session rather than spreading them across the week. The server processes one scrape at a time, so plan accordingly.

## Browser Resource Cleanup

After completing scraping sessions, clean up browser resources for optimal performance. The browser session persists between operations and may accumulate memory over time. For very long sessions, periodically restart the browser by calling open_readly_browser again. If the browser becomes unresponsive, use stop_scrape and restart. The browser window can be minimized during scraping to reduce desktop clutter. On server restart, the browser session is automatically recreated when needed.

## Multi-User Considerations

The server supports a single Readly account at a time through the browser session. All operations use the authenticated Readly session. Content matching uses the account's subscribed magazine list. The API settings are shared across all connected MCP clients. The scraping state is global and visible to all clients. For multi-user scenarios, consider running separate server instances with different Readly accounts.

## Magazine Discovery Workflow

Build a comprehensive magazine discovery and selection workflow. Start broad with topic-based searches using search_magazines. Review search results for relevant publications. Open promising magazines with open_latest_issue to verify content quality. List articles to see if the magazine's content matches your interests. Add matching magazines to your watch list for regular monitoring. Remove magazines that consistently fail to deliver relevant content. Periodically re-search for new magazines covering your research topics.

## Content Archiving Strategy

Develop a strategy for archiving scraped magazine content for long-term access. Save completed PDFs to a organized folder structure by magazine name and date. Extract article text for searchable text archives. Tag articles with topics and keywords for easy retrieval. Back up the archive directory to prevent data loss. Consider compressing older PDFs to save space. The server saves PDFs to ~/Desktop/readly/ by default; move completed files to your archive directory regularly.

## Scraping Etiquette and Best Practices

When scraping Readly magazines, follow responsible scraping practices. Set appropriate interval_seconds values to avoid overloading Readly's servers. Do not run multiple concurrent scrapes. Respect Readly's terms of service regarding automated access. Use scraping for personal archival and research purposes only. Do not redistribute scraped content. Monitor the scraping process and stop if any issues arise. The configurable delays and duplicate detection help maintain good citizenship.

## Content Matching Use Cases

The content matching feature supports several research use cases. For arXiv paper tracking, match paper titles against magazine articles to find popular science coverage. For competitor monitoring, match company names and product terms against business publications. For trend analysis, match industry keywords against technology and science magazines. For personal research, match specific topics of interest across your entire magazine collection. The query parameter accepts natural language for flexible matching.

## Understanding Scrape Status Messages

The get_status tool returns status messages that indicate the current state of the scraping process. "Idle" means no scrape is currently running. "Running" indicates pages are being actively captured. "Compiling PDF" means all pages are captured and the PDF is being generated. "Completed" means the PDF is ready. "Failed: No pages captured" means the scrape ended without capturing any pages, possibly due to browser issues or navigation failure. "Error: [message]" provides specific error information for troubleshooting.

## Restarting After Errors

If a scrape job encounters an error, follow these steps to recover. First, check the status message to understand the error. If the browser crashed, use open_readly_browser to restart it. If authentication was lost, check your READLY_AUTH_TOKEN or log in manually. Once the browser is working, start a new scrape with smart_scrape. The previous partial screenshots are discarded on restart. If the error persists, try restarting the entire server process.

## Performance Monitoring During Scraping

Monitor system performance during long scraping sessions to ensure reliable operation. Check available memory before starting large scrapes. Monitor CPU usage to ensure the browser has sufficient processing resources. Watch disk space for screenshot storage during the scrape. Use get_status to track progress and detect stalls. If performance degrades during a session, consider stopping the scrape, restarting the browser, and resuming with adjusted parameters. For very large magazines, consider splitting the scrape into multiple sessions.

## Batch Processing Strategy

For efficient batch processing of multiple magazines, follow a systematic approach. Process each magazine completely before moving to the next to minimize browser navigation overhead. For each magazine, open the latest issue, list articles, extract relevant articles, and optionally start a scrape for full PDF capture. Track which magazines have been processed using external notes or the server's status output. For research projects, use content matching to identify relevant magazines before committing to full extraction.

## Troubleshooting LLM Provider Connections

When LLM provider connections fail, verify the provider is running by accessing its API directly in a browser or curl. For Ollama, check http://localhost:11434/api/tags. For LM Studio, check http://localhost:1234/v1/models. For OpenAI-compatible providers, verify the base URL and API key are correct. The api_llm_status endpoint provides detailed diagnostics for the configured provider. If a provider is not detected, ensure it is running on the expected port and has not been configured to listen on a different interface.

## LLM Integration for Content Enhancement

The integrated LLM features can enhance your magazine research workflow. Use api_llm_chat to summarize long articles, translate content between languages, extract key points from technical articles, or generate research notes from magazine content. The chat endpoint connects to your configured local or cloud LLM provider, allowing AI-powered analysis of scraped magazine content without leaving the server environment.

## Multi-Magazine Workflow Planning

For research projects spanning multiple magazines, plan your workflow to minimize browser navigation overhead. Start by searching for all relevant magazines in one session using search_magazines. For each magazine, open the latest issue and list articles, deciding which to extract before moving to the next magazine. Use content matching for targeted article discovery across your watch list. Extract articles in priority order, starting with the most relevant publications. Compile all extracted articles into your research database after the session.

## Tutorial 11: Multi-Issue Research Compilation

Gather articles from multiple magazine issues on a specific research topic and compile the findings.

**Steps:**
1. Search for relevant magazines: search_magazines(query="artificial intelligence")
2. Open the first magazine and list articles: open_latest_issue(magazine_name="Wired UK"), list_articles()
3. Extract relevant articles: extract_article_text(article_index=0)
4. Open a second magazine and extract: open_latest_issue(magazine_name="MIT Technology Review"), list_articles(), extract_article_text(article_index=1)
5. Use content matching to find all AI articles: api_content_match(magazines=["Wired UK", "MIT Technology Review", "New Scientist"], query="deep learning", max_per_magazine=5)

## Tutorial 12: Fleet Pipeline Integration

Integrate readly-mcp with fleet monitoring for automated magazine content tracking.

**Steps:**
1. Set up the server with READLY_AUTH_TOKEN configured
2. Verify fleet integration: api_pipeline_liveness()
3. Set up scheduled scraping for watch-list magazines using the pipeline liveness endpoint for monitoring
4. Use api_content_match for automated article discovery matching research paper topics
5. Check pipeline health regularly: api_health(), api_pipeline_liveness()

## Browser Management Best Practices

The Playwright browser opens in headed mode by default, which means a visible browser window appears on screen. Do not close this browser window manually; the server manages its lifecycle. If the browser crashes or becomes unresponsive, use stop_scrape() and then open_readly_browser() to restart. Cookies are persisted in the user_data directory, so manual login is only needed on first run or when the session expires.

For optimal scraping performance, close unnecessary applications to free system resources. The browser requires significant memory for large magazine issues. Use the stop_scrape() tool if the scraping appears stuck on a particular page, then restart with adjusted parameters.

## Performance Tips

Scraping speed is primarily determined by the interval_seconds parameter. For quick previews, use 30-60 seconds. For full archival quality, use 120-180 seconds to ensure pages load completely. The max_pages parameter should match the typical size of the magazine being scraped. Most magazines are 80-200 pages. Set max_pages higher than expected to ensure full capture; the duplicate detection will stop automatically at the end of the issue.

PDF compilation time depends on the number of pages captured. A 100-page magazine typically compiles in 10-30 seconds. Ensure sufficient free disk space for both the intermediate screenshots and the final PDF. Screenshots are stored temporarily and deleted after PDF compilation.

## LLM Integration Tips

When using the LLM chat features, ensure your provider is running before calling the chat endpoints. Ollama can be started via the command line or service manager. LM Studio runs as a desktop application and must be launched with a model loaded before the API becomes available. The api_llm_providers endpoint is useful for discovering which providers are running without needing to remember port numbers.

For best results with content matching, use specific, focused queries rather than broad topics. The matching algorithm works best with distinctive terms that are likely to appear in article titles and summaries. For arXiv paper title matching, use the exact paper title as the query string.

## Common Issues and Solutions

If the browser fails to launch, check that Playwright is properly installed. Run playwright install chromium to ensure the browser binary is available. If Readly login fails repeatedly, delete the user_data directory and restart the browser for a fresh login session. If scraping produces duplicate or incomplete pages, increase the interval_seconds to give pages more time to load. If the PDF compilation fails, check available disk space and that the output directory exists. If LLM providers are not detected, verify they are running and accessible on the expected ports.

**Q: How do I find my Readly auth token?**
A: The token can be extracted from browser cookies after logging in to Readly.

**Q: What file formats are supported?**
A: Screenshots are PNG, compiled output is PDF, article text is returned as structured JSON.

**Q: Can I schedule automatic scrapes?**
A: The server supports manual triggering only. For scheduled scraping, integrate with external scheduling tools like cron or Task Scheduler.

**Q: How do I update my Readly auth token?**
A: Use api_set_auth_token at any time without restarting. The new token is used immediately for subsequent operations.

**Q: What happens if the browser crashes during a scrape?**
A: The scrape job enters an error state. Check the status with get_status(), then restart with open_readly_browser() and smart_scrape(). Previous partial screenshots are discarded on restart.
**Q: Can I run the server on a headless system?**
A: Readly magazine scraping requires a visible browser window for proper page rendering. Headless mode is not supported for this use case.
