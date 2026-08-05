import pytest

from app.infrastructure.cache.rate_limit_store import RateLimitStore


@pytest.fixture
def store(monkeypatch):
    s = RateLimitStore()
    monkeypatch.setattr(s, "_client", lambda: None)
    return s


def test_memory_fallback_counts_within_window(store):
    assert store.add("user:1", 1000.0, 60) == 1
    assert store.add("user:1", 1001.0, 60) == 2
    assert store.add("user:1", 1002.0, 60) == 3


def test_memory_fallback_drops_expired_entries(store):
    store.add("user:1", 1000.0, 60)
    store.add("user:1", 1001.0, 60)
    assert store.add("user:1", 1070.0, 60) == 1


def test_memory_fallback_scopes_keys(store):
    store.add("user:1", 1000.0, 60)
    assert store.add("user:2", 1000.0, 60) == 1
    assert store.add("user:1", 1001.0, 60) == 2
