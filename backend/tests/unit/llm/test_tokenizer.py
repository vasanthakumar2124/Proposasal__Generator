from app.llm.tokenizer import estimate_tokens, truncate_to_max_tokens, count_messages_tokens


class TestTokenizer:
    def test_estimate_simple(self):
        assert estimate_tokens("hello world") == 2

    def test_estimate_empty(self):
        assert estimate_tokens("") == 1

    def test_truncate_too_long(self):
        text = "a" * 1000
        result = truncate_to_max_tokens(text, 50)
        assert len(result) < len(text)

    def test_truncate_short_enough(self):
        text = "short"
        assert truncate_to_max_tokens(text, 100) == "short"

    def test_count_messages(self):
        msgs = [
            {"role": "user", "content": "hello world"},
            {"role": "assistant", "content": "hi there"},
        ]
        assert count_messages_tokens(msgs) == 4
