import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_playwright():
    """
    Mocks the Playwright objects to avoid opening real browsers during tests.
    """
    mock_p = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    # Chain setup
    mock_p.chromium.launch_persistent_context.return_value = mock_context
    mock_context.pages = [mock_page]
    mock_context.new_page.return_value = mock_page

    return {"playwright": mock_p, "context": mock_context, "page": mock_page}


@pytest.fixture
def mock_browser_manager(mock_playwright):
    """
    Returns a BrowserManager instance with mocked internals.
    """
    # Import locally to avoid side effects if not installed
    from readly_mcp.core.browser import BrowserManager

    manager = BrowserManager()
    manager.playwright = mock_playwright["playwright"]
    manager.context = mock_playwright["context"]
    manager.page = mock_playwright["page"]
    return manager
