from app.llm.models import MODEL_REGISTRY, TASK_MODEL_MAP


class TestNvidiaIntegration:
    def test_nvidia_registered_with_fast_model(self):
        cfg = MODEL_REGISTRY["nvidia"]
        assert cfg["default"].model == "meta/llama-3.1-8b-instruct"
        assert cfg["fast"].model == "meta/llama-3.1-8b-instruct"
        assert cfg["default"].provider == "nvidia"

    def test_medium_chain_has_nvidia_after_groq_default(self):
        chain = TASK_MODEL_MAP["medium"]
        assert ("nvidia", "default") in chain
        assert chain.index(("groq", "default")) < chain.index(("nvidia", "default")) < chain.index(("groq", "fast"))

    def test_simple_chain_has_nvidia_fast(self):
        assert ("nvidia", "fast") in TASK_MODEL_MAP["simple"]

    def test_nvidia_call_raises_on_empty_content(self, monkeypatch):
        from app.llm import client as client_mod
        from app.config.settings import settings

        class FakeChoice:
            finish_reason = "length"
            class FakeMessage:
                content = None
            message = FakeMessage()

        class FakeResponse:
            choices = [FakeChoice()]

        class FakeCompletions:
            def create(self, **kwargs):
                return FakeResponse()

        class FakeChat:
            completions = FakeCompletions()

        class FakeOpenAI:
            def __init__(self, api_key=None, base_url=None, timeout=None):
                pass

            chat = FakeChat()

        import openai as openai_mod

        monkeypatch.setattr(openai_mod, "OpenAI", FakeOpenAI)
        import pytest

        c = client_mod.LLMClient()
        with pytest.raises(RuntimeError, match="no content"):
            c._call_nvidia("meta/llama-3.3-70b-instruct", "prompt", 10, 0.3)
