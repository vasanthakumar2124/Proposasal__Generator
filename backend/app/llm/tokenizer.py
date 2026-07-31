import re

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
    _have_tiktoken = True
except Exception:
    _have_tiktoken = False


def estimate_tokens(text: str) -> int:
    if _have_tiktoken:
        return max(1, len(_enc.encode(text)))
    rough = len(text) / 4
    return max(1, int(rough))


def truncate_to_max_tokens(text: str, max_tokens: int) -> str:
    if max_tokens <= 0:
        return ""
    estimated = estimate_tokens(text)
    if estimated <= max_tokens:
        return text
    if _have_tiktoken:
        tokens = _enc.encode(text)
        return _enc.decode(tokens[:max_tokens])
    ratio = max_tokens / estimated
    target_chars = int(len(text) * ratio * 0.9)
    return text[:target_chars]


def count_messages_tokens(messages: list[dict]) -> int:
    total = 0
    for msg in messages:
        total += estimate_tokens(msg.get("content", ""))
    return total
