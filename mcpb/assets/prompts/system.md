# readly-mcp — MCP Server Capabilities

## Server Overview

readly-mcp is an MCP server for scraping Readly magazine content, providing automated magazine browsing, article extraction, PDF compilation, and content matching. It integrates with Readly's web platform through Playwright browser automation to access digital magazines, extract articles, and compile them into PDF documents. The server also includes a comprehensive FastAPI REST bridge with LLM integration for local AI model connectivity.

The server uses Playwright for browser automation to navigate Readly's magazine reader interface, capture page screenshots, compile PDFs from magazine issues, extract article text and metadata, and search the Readly library. It includes a scraping state manager that tracks progress, handles page turning, detects duplicate pages (end of issue), and manages asynchronous scrape jobs. The REST API bridge exposes all MCP tools as HTTP endpoints plus additional features for LLM provider management, content matching, and pipeline health monitoring.

Key features include Playwright-based browser automation for Readly magazine access, automated scraping with page capture and PDF compilation, article text extraction with configurable indexing, magazine search and library browsing, content matching against watch-list magazines, LLM integration with Ollama, LM Studio, and OpenAI-compatible providers, fleet pipeline health monitoring, and settings management via REST API.

## Tools

### open_readly_browser
Opens the Playwright browser and navigates to Readly. Auto-logs in if READLY_AUTH_TOKEN environment variable is set. First run without token requires manual login (cookies are persisted via user_data directory).

**Return Format:** String message indicating browser opened with or without login.

### smart_scrape
Starts the background scraping process for a named magazine issue. Opens the issue, captures each page as a screenshot, detects duplicate pages (end of issue), turns pages, and compiles all screenshots into a PDF saved to ~/Desktop/readly/.

**Parameters:** issue_name string (required, e.g. "The Economist - March 2026"), interval_seconds float (default 120, time between page turns), max_pages int (default 200, max pages to scrape)

**Return Format:** String message confirming scrape started with issue name.

### get_status
Returns the current status of the active or most recent scraping job.

**Return Format:** Dict with status string, is_running bool, issue string, current_page int, pages_captured int

### stop_scrape
Stops the current scraping job gracefully. Sets the stop flag, allowing the current page to finish before halting.

**Return Format:** String confirming stop signal sent or no job running.

### open_latest_issue
Searches Readly and opens the latest issue for a magazine by name. Requires the browser to be initialized.

**Parameters:** magazine_name string (required)

**Return Format:** Dict with issue title, URL, publication date, and page count.

### read_all_articles
Batch-extracts full text for articles on the current magazine issue page. Reads article content by iterating through available articles.

**Parameters:** max_articles int (default 10)

**Return Format:** Dict with article count and list of article text objects.

### list_articles
Parses the current Readly magazine page and extracts article titles with URLs. Requires browser to be on a magazine issue page.

**Return Format:** Dict with article list including titles, URLs, and section information.

### extract_article_text
Extracts the full text of an article from the current magazine issue by index. Call list_articles first to get available articles and their indices.

**Parameters:** article_index int (default 0, 0-based index of the article)

**Return Format:** Dict with article title, text content, and metadata.

### search_magazines
Searches Readly for magazines matching a keyword query. Returns matching magazine titles and metadata.

**Parameters:** query string (required, e.g. "economist", "science", "cooking")

**Return Format:** Dict with search results including magazine names, issue counts, and availability.

### list_library
Scrapes the Readly newsstand for all available magazines and issues in your library.

**Return Format:** Dict with library contents organized by category or alphabetically.

### API Tools (REST Bridge)

The server exposes all MCP tools as REST API endpoints plus additional functionality:

**api_get_status** (GET /api/status): Current scrape job status
**api_health** (GET /api/health): Server health check with version
**api_list_tools** (GET /api/tools): List all registered MCP tools
**api_start_scrape** (POST /api/scrape/start): Start a scrape job
**api_stop_scrape** (POST /api/scrape/stop): Stop the current scrape
**api_open_latest** (GET /api/magazines/latest): Open latest magazine issue
**api_read_all_articles** (GET /api/articles/read-all): Extract all articles text
**api_list_articles** (GET /api/articles/list): List magazine articles
**api_extract_article** (GET /api/articles/extract): Extract single article by index
**api_search_magazines** (GET /api/magazines/search): Search magazines by query
**api_list_library** (GET /api/library): List full magazine library
**api_open_magazine** (GET /api/magazines/open): Open a specific magazine URL
**api_content_match** (POST /api/content/match): Search watch-list magazines for articles matching a query
**api_pipeline_liveness** (GET /api/pipeline/liveness): Fleet health probe endpoint
**api_set_auth_token** (POST /api/auth/token): Set Readly auth token for session
**api_update_settings** (POST /api/settings): Update runtime settings
**api_get_settings** (GET /api/settings): Get current LLM settings
**api_update_llm_settings** (POST /api/settings/llm): Update LLM provider settings
**api_list_llm_models** (GET /api/llm/models): List models from configured LLM provider
**api_llm_chat** (POST /api/llm/chat): Send chat message to configured LLM
**api_llm_providers** (GET /api/llm/providers): Discover local LLM providers
**api_llm_status** (GET /api/llm/status): Check LLM provider connectivity

### Transport Tools
**main_stdio**: Run MCP server in stdio mode
**main_http**: Run MCP server in HTTP mode
**main_sse**: Run MCP server in SSE mode

## Configuration

### Environment Variables
- READLY_AUTH_TOKEN: Readly authentication token for auto-login
- READLY_SCRAPE_INTERVAL: Default interval between page turns (seconds)
- READLY_MAX_PAGES: Default maximum pages to scrape
- OLLAMA_URL: Ollama API URL (default: http://localhost:11434)
- OLLAMA_MODEL: Default Ollama model
- LMSTUDIO_URL: LM Studio API URL (default: http://localhost:1234/v1)
- LMSTUDIO_MODEL: Default LM Studio model
- LLM_PROVIDER: Active LLM provider (ollama, lmstudio, openai)
- LOCAL_LLM_URL: OpenAI-compatible API URL
- LOCAL_LLM_KEY: API key for OpenAI-compatible provider
- WEB_PORT: Port for REST API bridge (default: 10863)

### Storage
- Screenshots are stored temporarily during scraping
- PDFs are saved to ~/Desktop/readly/
- Cookies persist in user_data directory for session maintenance
- Settings are stored in environment variables (session-level)

## Data Sources

### Readly Platform
The server interacts with Readly's web interface through Playwright. Authentication is handled via READLY_AUTH_TOKEN or manual login (cookies persisted). The server respects page load times and maintains a realistic reading/scraping pace to avoid rate limiting.

### Local LLM Providers
The server auto-discovers and connects to local LLM providers:
- Ollama on port 11434
- LM Studio on port 1234
- OpenAI-compatible endpoints

## Error Handling

All tools return structured error responses:
- MCP tools return dict with success bool and error messages
- REST API endpoints return appropriate HTTP status codes
- Scraping errors include status updates and recovery guidance
- Browser automation failures include diagnostic information
- Common errors: authentication failure, page timeout, browser crash

## Performance Characteristics

- Browser launch: 3-8 seconds
- Page capture: 2-5 seconds per page
- PDF compilation: 10-30 seconds for full magazine
- Article extraction: 5-15 seconds per article
- Magazine search: 5-20 seconds depending on query
- LLM queries: 2-30 seconds depending on model
- Health checks: <100ms
- Content matching: 30-120 seconds for multi-magazine search

## Security Considerations

- READLY_AUTH_TOKEN stored in environment variable, not persisted to disk
- Auth token can be set dynamically via API without restart
- Browser automation runs in non-headless mode by default (requires GUI)
- Local LLM connections are to localhost only
- No external API calls beyond Readly and local LLM providers
- PDF output stored locally in user's Desktop directory
- Browser cookies are persisted in user_data directory for session continuity
- LLM API keys are stored in environment variables only, never in tool responses

## Browser Automation Architecture

The browser_manager module manages the Playwright browser lifecycle. It supports launching Chromium in headed mode for interactive Readly access. The browser handles authentication through READLY_AUTH_TOKEN or manual login with cookie persistence. Page navigation includes magazine search, issue opening, article listing, and text extraction. Screenshot capture supports full-page and viewport captures for magazine page preservation. Page turning is automated through click interactions with configurable delays between pages.

The scraping worker runs as an asynchronous background task, managing the complete lifecycle from browser initialization to PDF compilation. It tracks progress through the scraping_state dictionary which stores the current page number, total pages captured, issue name, status messages, and screenshots list. The worker implements duplicate page detection by comparing consecutive screenshot file hashes to automatically detect the end of an issue. Error handling includes browser crash recovery, network timeout management, and graceful cancellation via stop flag.

## PDF Compilation System

The PDF compilation system takes captured screenshots and assembles them into a single PDF document. It uses the create_pdf function which processes the screenshot list in order, inserting each page as a full-page image in the PDF. The output PDF is saved to ~/Desktop/readly/ with the issue name as filename. The compilation happens after all pages are captured or when scraping is stopped early. The system handles variable page counts and generates appropriately sized PDF documents matching the original magazine layout.

## Content Matching Engine

The content matching system (api_content_match) searches watch-list magazines on Readly for articles matching a search query. It uses the browser to navigate to each watch-list magazine, extract article titles and summaries, and score each article against the query string using keyword matching and contextual relevance. Results are returned with matched article titles, relevance scores, and direct URLs for the user to read. This is particularly useful for research workflows where users want to find magazine articles related to specific topics like arXiv paper titles or news topics.

## LLM Provider Integration Detail

The LLM integration supports three provider types with distinct API patterns. Ollama integration uses the /api/chat endpoint with streaming disabled, supporting models like llama3.2, qwen3.5, and gemma. LM Studio integration uses the OpenAI-compatible /v1/chat/completions endpoint with configurable base URL. OpenAI-compatible integration allows any endpoint following the OpenAI API format including custom endpoints and API gateways, supporting models like gpt-4o-mini via configurable base URL and API key.

The api_llm_providers endpoint auto-discovers available providers by probing standard ports on localhost. It checks port 11434 for Ollama and port 1234 for LM Studio, querying each for available models. The discovery results include provider IDs, display labels, base URLs, model lists, and whether the provider requires an API key. This enables zero-configuration setup where the server automatically finds and connects to available local LLM infrastructure.

## API Endpoint Reference

The REST API is organized into functional groups. System endpoints provide health monitoring and tool listing. Scraping endpoints manage the magazine scraping lifecycle. Magazine endpoints handle issue discovery and navigation. Article endpoints provide content extraction. Library endpoints manage the magazine collection. Content endpoints handle intelligent search and matching. Auth endpoints manage authentication. Settings endpoints provide runtime configuration. LLM endpoints handle AI model integration.

Each API endpoint has specific request and response formats. POST endpoints accept JSON request bodies. GET endpoints use query parameters for filtering and configuration. Error responses follow consistent format with error message and optional detail field. Authentication errors return 401 status codes. Validation errors return 400 status codes with field-level details. Server errors return 500 status codes.

## Pipeline Health Monitoring

The api_pipeline_liveness endpoint provides comprehensive fleet health monitoring. It returns the authentication token status, browser active state, current scrape job status, last poll statistics, and any active alerts. Alerts include missing authentication tokens and active scrape jobs that may need monitoring. This endpoint is designed for integration with fleet monitoring systems like the aiwatcher-mcp pipeline.

## Rate Limiting and Polite Scraping

The scraping system implements polite scraping practices. Configurable delays between page turns prevent overwhelming the Readly server. Jitter adds randomness to timing patterns. Duplicate page detection prevents unnecessary captures. Browser session management maintains consistent authentication state. Error recovery includes automatic retry on transient failures. The system respects Readly's terms of service through configurable interaction patterns.

## Magazine Search Algorithms

The search functionality uses Readly's internal search engine through the web interface. When a search query is submitted, the browser navigates to Readly's search page, enters the query, and waits for results to load. The results are parsed to extract magazine names, issue counts, publication frequency, cover images, and subscription availability. The search supports fuzzy matching and returns results ranked by relevance according to Readly's algorithm. Common search patterns include searching by magazine title for exact matches, by topic for category browsing, and by publisher for brand-specific discovery.

## Article Extraction Pipeline

When extracting article text, the browser navigates to the article page within the magazine viewer, waits for the text content to render, and extracts the article body using DOM parsing. The extraction captures the article title, author if available, publication date, body text with paragraph structure, and any inline images or captions. The read_all_articles operation iterates through all available articles on the current page, extracting each one sequentially. The extract_article_text operation targets a specific article by its index in the article list.

## Error Recovery Mechanisms

The server implements several error recovery mechanisms for robust operation. Browser crash recovery detects when the Playwright browser process has terminated and provides clear error messages with restart instructions. Network timeout recovery catches stalled page loads and reports the specific URL that timed out. Authentication expiry detection flags when the Readly session has expired and suggests re-authentication. PDF compilation error handling reports the specific page that caused compilation failure.

## Session Persistence

Browser sessions are persisted through cookies stored in the user_data directory. This enables authentication state to survive server restarts. The session persistence directory is created automatically on first browser launch. If authentication issues occur, deleting the user_data directory forces a fresh login. The session data includes Readly login cookies, search history, and magazine access tokens.

## State Management

The server maintains scraping state in a global dictionary that tracks the current operation. The is_running flag indicates whether a scrape is active and prevents concurrent scrape operations. The current_page counter tracks progress through the magazine. The screenshots list accumulates captured page images for PDF compilation. The status string provides a human-readable status message. The stop_flag enables graceful cancellation of running operations. This state model ensures clean operation lifecycle management without requiring a database.

## Browser Resource Management

The Playwright browser process consumes significant system resources when running. Each magazine page capture requires memory for rendering and screenshot storage. For extended scraping sessions, monitor system resource usage and adjust parameters accordingly. The browser session persists across operations to avoid repeated launch overhead. If memory usage becomes excessive, use stop_scrape to end the current operation and restart the browser with open_readly_browser to clear accumulated state.

## Debugging and Diagnostics

The server provides several diagnostic tools for troubleshooting. The get_status endpoint returns the complete scraping state for debugging stalled operations. The api_pipeline_liveness endpoint provides fleet integration diagnostics including authentication status, browser health, and scrape job state. The api_health endpoint confirms basic server functionality. For LLM-related issues, the api_llm_status endpoint tests provider connectivity and model availability. The api_llm_providers endpoint discovers all available local LLM providers and their models.

## Scrape Job Lifecycle

Each scrape job follows a defined lifecycle. When smart_scrape is called, the job enters the starting state where it initializes the browser and navigates to the target issue. Once the issue is loaded, the job enters the running state and begins capturing pages sequentially. Each page capture goes through load wait duration, screenshot capture, duplicate detection, and page turning. If the stop flag is set, the job enters the stopping state, completes the current page, then moves to compilation. After all pages are captured, the job enters the compiling state where screenshots are assembled into the final PDF. On completion, the job enters the completed state. If any error occurs, the job enters the error state with a descriptive message.

## Browser Profile Isolation

The server maintains isolated browser profiles through the user_data directory. Each Readly login session is stored in its own profile directory, preventing conflicts between different authentication attempts. The profile stores cookies, local storage, and session data specific to Readly. If authentication issues arise, clearing the profile directory forces a fresh login. The profile is created automatically on first browser launch and persists across server restarts.

## Dependency Graph

The server depends on several Python packages for its functionality. FastMCP provides the MCP server framework with tool registration, resource mounting, and transport handling. FastAPI provides the REST API bridge layer. Uvicorn serves the FastAPI application with async workers. Playwright provides browser automation for Readly interaction. httpx provides async HTTP client for LLM provider communication. The server validates availability of key dependencies at startup and reports missing packages in health check responses.

## Multi-Transport Architecture

The server supports three MCP transport modes for flexible deployment. The stdio transport runs the MCP server over standard input/output, ideal for direct client integration. The HTTP transport mounts the MCP handler at /mcp within the FastAPI application, enabling HTTP-based tool access. The SSE transport provides server-sent events for streaming responses. All three transports expose the same tool set and respond to the same MCP protocol messages. Transport selection is handled by the main function based on the MCP_TRANSPORT environment variable.

## Settings Persistence

Server settings are persisted through environment variables for the current session. The api_set_auth_token endpoint stores the authentication token in the process environment for immediate use. The api_update_settings endpoint modifies runtime configuration in the environment. The api_update_llm_settings endpoint configures LLM provider connections. Settings are not persisted to disk and reset when the server restarts, except for the .env file when using the file-based configuration mechanism.

## Error Classification

The server classifies errors into categories for consistent handling. Authentication errors occur when READLY_AUTH_TOKEN is missing or invalid, requiring token refresh or manual login. Navigation errors occur when the browser cannot reach the expected Readly page, requiring network or URL verification. Timeout errors occur when page operations exceed waiting periods, requiring interval adjustments. Browser errors occur when Playwright encounters issues, requiring browser restart. Compilation errors occur during PDF generation, requiring disk space or file permission verification.

## Browser Automation Commands

The browser_manager supports a range of automation commands for interacting with Readly. The start_browser command launches Chromium with configured options including user data directory and viewport size. The go_to_readly command navigates to the Readly login page and handles authentication. The turn_page_right command simulates a right-swipe to advance to the next magazine page. The take_page_screenshot command captures the current page image. The list_articles command parses the article list from the current page DOM. The extract_article_text command reads article content from the article viewer page.

## Scraping Performance Factors

Several factors affect scraping speed and reliability. Internet connection speed determines how quickly magazine pages load in the browser. Readly server response time varies by time of day and server load. Magazine complexity affects page render time; image-heavy pages take longer to load. Browser resource usage accumulates during long scraping sessions. System resource availability impacts page capture speed. The interval_seconds parameter should be tuned based on these factors for optimal results.

## Magazine Navigation Flow

When opening a magazine issue through open_latest_issue, the browser performs a multi-step navigation sequence. It searches Readly for the magazine name, selects the first matching result, navigates to the magazine's issue list, identifies the most recent issue, opens the issue reader, waits for the first page to render, and returns the issue metadata. Each step includes timeout protection and error handling for broken navigation paths.

## Fleet Integration Endpoints

The api_pipeline_liveness endpoint is designed for integration with fleet monitoring systems like aiwatcher-mcp. It returns structured health data including auth_token_set boolean for READLY_AUTH_TOKEN configuration status, browser_active boolean for current browser session state, scrape_status string for current job state, last_poll dict with recent activity metrics, and alerts list for any active warnings. This endpoint enables automated monitoring of readly-mcp as part of a larger fleet pipeline.

## Magazine Metadata Extraction

When listing articles or extracting content, the server captures available metadata. Article metadata includes the title as displayed on the magazine page, the publication date of the issue, the section or category within the magazine, the author name if available, and the article URL within the Readly reader. The metadata is returned alongside the extracted text content for reference and organization purposes.

## Content Matching Algorithm

The content matching engine scores articles against query terms using multiple signals. Title matching scores how well the article title matches the query keywords. Summary matching checks the article summary or excerpt for relevance. Keyword frequency analysis counts how often query terms appear in the article metadata. The combined relevance score helps prioritize the most relevant articles from each magazine. The max_per_magazine parameter limits results to avoid overwhelming the response with many marginal matches from a single publication.

## Magazine Content Matching Engine

The content matching system compares query strings against article titles and summaries from watch-list magazines. It uses keyword matching and contextual relevance scoring to identify relevant articles. The matching process involves navigating to each magazine's latest issue, extracting article metadata, and scoring each article against the query. Results are sorted by relevance score and returned with article details. The system supports multiple watch-list magazines in a single query and configurable results per magazine.

## Data Flow Architecture

Data flows through the server in a structured pipeline. The MCP tools layer receives tool calls from connected clients and routes them to the appropriate handler. The browser_manager handles all Playwright interactions with Readly's web interface. The scraping_state dictionary maintains current operation state across asynchronous tasks. The PDF compiler transforms captured screenshots into the final output document. The REST API bridge provides HTTP access to all MCP tools and additional management endpoints. The LLM integration layer manages connections to local and remote AI providers for chat and discovery features.
