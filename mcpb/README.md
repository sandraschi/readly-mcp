# readly-mcp (MCPB Bundle)

MCP server for scraping Readly magazines

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "readly-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "readly_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **open_readly_browser**: open_readly_browser
- **smart_scrape**: smart_scrape
- **get_status**: get_status
- **stop_scrape**: stop_scrape
- **open_latest_issue**: open_latest_issue
- **read_all_articles**: read_all_articles
- **list_articles**: list_articles
- **extract_article_text**: extract_article_text
- **search_magazines**: search_magazines
- **list_library**: list_library
- **api_get_status**: api_get_status
- **api_health**: api_health
- **api_list_tools**: api_list_tools
- **api_start_scrape**: api_start_scrape
- **api_stop_scrape**: api_stop_scrape
- **api_open_latest**: api_open_latest
- **api_read_all_articles**: api_read_all_articles
- **api_list_articles**: api_list_articles
- **api_extract_article**: api_extract_article
- **api_search_magazines**: api_search_magazines
- **api_list_library**: api_list_library
- **api_open_magazine**: api_open_magazine
- **api_content_match**: Search watch-list magazines on Readly for articles matching a query (e.g. arXiv paper title).
- **api_pipeline_liveness**: Fleet probe: auth token, browser, scrape job state.
- **api_set_auth_token**: Set the Readly auth token (stored in env, not persisted to disk).
- **api_update_settings**: Update runtime settings (stored in env for current session).
- **api_get_settings**: Return current LLM settings.
- **api_update_llm_settings**: Update LLM provider settings for the session.
- **api_list_llm_models**: List available models from the configured LLM provider.
- **api_llm_chat**: Send a chat message to the configured LLM.
- **api_llm_providers**: Discover local LLM providers (Ollama, LM Studio) and their models.
- **api_llm_status**: Check connectivity to the configured LLM provider.
- **main_stdio**: main(stdio)
- **main_http**: main(http)
- **main_sse**: main(sse)

## Requirements

- Python 3.12+
- uv
