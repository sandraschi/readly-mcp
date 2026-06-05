from readly_mcp.core.browser import _quality_check_articles


def test_quality_check_accepts_article_links():
    raw = [
        {"title": "Quantum chips reach new milestone", "url": "https://www.readly.com/read/x"},
        {"title": "AI safety frameworks compared", "url": "https://www.readly.com/read/y"},
    ]
    out = _quality_check_articles(raw)
    assert not out["extraction_failed"]
    assert len(out["articles"]) == 2


def test_quality_check_rejects_nav_elements():
    raw = [
        {"title": "Home", "url": ""},
        {"title": "My Library", "url": ""},
        {"title": "Search", "url": ""},
    ]
    out = _quality_check_articles(raw)
    assert out["extraction_failed"]
    assert out["reason"] in ("no_articles_after_filter", "nav_elements_detected")
