"""
Unit tests for promas.search_backends abstraction
"""

from promas.search_backends import (
    BingBrowserSearchBackend,
    BraveSearchBackend,
    SerpApiSearchBackend,
    decode_bing_redirect,
    get_search_backend,
)


def test_decode_bing_redirect():
    raw_direct = "https://www.apple.com/iphone-16-pro/"
    assert decode_bing_redirect(raw_direct) == raw_direct

    # Invalid / empty
    assert decode_bing_redirect(None) is None
    assert decode_bing_redirect("") is None


def test_brave_backend_availability(monkeypatch):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    backend = BraveSearchBackend()
    assert backend.is_available() is False
    assert backend.is_experimental is False

    monkeypatch.setenv("BRAVE_API_KEY", "test_key_123")
    backend_with_key = BraveSearchBackend()
    assert backend_with_key.is_available() is True


def test_serpapi_backend_availability(monkeypatch):
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    backend = SerpApiSearchBackend()
    assert backend.is_available() is False
    assert backend.is_experimental is False

    monkeypatch.setenv("SERPAPI_API_KEY", "test_key_456")
    backend_with_key = SerpApiSearchBackend()
    assert backend_with_key.is_available() is True


def test_get_search_backend_prefers_api(monkeypatch):
    # No keys -> browser fallback
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
    backend = get_search_backend()
    assert isinstance(backend, BingBrowserSearchBackend)
    assert backend.is_experimental is True

    # With Brave Key -> Brave
    monkeypatch.setenv("BRAVE_API_KEY", "dummy_brave")
    backend_brave = get_search_backend()
    assert isinstance(backend_brave, BraveSearchBackend)

    # With SerpAPI Key only -> SerpAPI
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.setenv("SERPAPI_API_KEY", "dummy_serpapi")
    backend_serp = get_search_backend()
    assert isinstance(backend_serp, SerpApiSearchBackend)
