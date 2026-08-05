import uuid

from app.llm.cache import LLMCache


class TestLLMCache:
    def test_cache_miss_then_hit(self):
        cache = LLMCache()
        cache._enabled = True
        prompt = f"test prompt {uuid.uuid4()}"
        model = "groq:default"
        assert cache.get(prompt, model) is None
        cache.set(prompt, model, "response", ttl_hours=1)
        assert cache.get(prompt, model) == "response"
        cache.delete(prompt, model)

    def test_cache_disabled(self):
        cache = LLMCache()
        cache._enabled = False
        prompt = "test"
        cache.set(prompt, "x", "resp")
        assert cache.get(prompt, "x") is None

    def test_cache_expiry(self):
        cache = LLMCache()
        cache._enabled = True
        prompt = "expiry_test"
        cache.set(prompt, "x", "old", ttl_hours=-2)
        assert cache.get(prompt, "x") is None
