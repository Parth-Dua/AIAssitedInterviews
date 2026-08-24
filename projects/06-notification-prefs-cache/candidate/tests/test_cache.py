from app.cache.cache import Cache


def test_cache_miss_returns_none():
    cache = Cache()
    assert cache.get("missing") is None


def test_cache_set_then_get_returns_value():
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"


def test_cache_delete_removes_entry():
    cache = Cache()
    cache.set("key", "value")
    cache.delete("key")
    assert cache.get("key") is None


def test_cache_entries_expire_after_ttl():
    """Feature request: cache entries should support a TTL so they expire
    automatically even if a write's invalidation is somehow missed
    elsewhere (defense in depth). Uses an injectable fake clock instead of
    a real sleep so the test is deterministic and fast.
    """
    fake_now = [0.0]
    cache = Cache(now_fn=lambda: fake_now[0])

    cache.set("key", "value", ttl_seconds=10)
    assert cache.get("key") == "value"

    fake_now[0] = 20.0  # well past the 10-second TTL
    assert cache.get("key") is None, "entry should have expired and been evicted"
