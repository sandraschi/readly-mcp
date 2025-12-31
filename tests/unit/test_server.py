import pytest
from unittest.mock import MagicMock, patch


def test_browser_manager_structure(mock_browser_manager):
    """
    Verifies browser manager methods exist and use the mock.
    """
    # Simulate start
    bm = mock_browser_manager
    page = bm.start_browser()
    assert page == bm.page

    # Simulate nav
    bm.go_to_readly()
    bm.page.goto.assert_called_with("https://go.readly.com")


def test_pdf_creation_structure():
    """
    Verifies PDF import and mock interaction.
    """
    from readly_mcp.core.pdf import create_pdf

    with (
        patch("readly_mcp.core.pdf.FPDF") as MockFPDF,
        patch("readly_mcp.core.pdf.Image") as MockImage,
    ):
        create_pdf(["dummy.png"], "out.pdf")
        MockFPDF.return_value.output.assert_called()


def test_server_tools_exist():
    """
    Verifies that the MCP server object has the expected tools registered.
    """
    from readly_mcp.server import mcp

    tools = [t.name for t in mcp._tools]
    assert "open_readly_browser" in tools
    assert "smart_scrape" in tools
    assert "get_status" in tools
