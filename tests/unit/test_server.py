import asyncio
import pytest
from unittest.mock import patch


@pytest.mark.skip(reason="conftest mock needs async overhaul for Playwright 1.40+")
def test_browser_manager_structure(mock_browser_manager):
    bm = mock_browser_manager
    assert bm.page is not None


def test_pdf_creation_structure():
    from readly_mcp.core.pdf import create_pdf

    with (
        patch("readly_mcp.core.pdf.FPDF") as MockFPDF,
        patch("readly_mcp.core.pdf.Image") as _MockImage,
    ):
        create_pdf(["dummy.png"], "out.pdf")
        MockFPDF.return_value.output.assert_called()


def test_server_tools_exist():
    from readly_mcp.server import mcp

    tools = asyncio.run(mcp.list_tools())
    tool_names = {t.name for t in tools}

    expected = {
        "open_readly_browser", "smart_scrape", "get_status", "stop_scrape",
        "list_articles", "extract_article_text", "search_magazines",
        "open_latest_issue", "read_all_articles",
    }
    missing = expected - tool_names
    assert not missing, f"Missing tools: {missing}"
