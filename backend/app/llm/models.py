from dataclasses import dataclass, field
from typing import Literal


TaskComplexity = Literal["simple", "medium", "complex"]


@dataclass
class ModelConfig:
    provider: str
    model: str
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0


MODEL_REGISTRY: dict[str, dict[str, ModelConfig]] = {
    "groq": {
        "fast": ModelConfig("groq", "llama-3.1-8b-instant", 0.00000010, 0.00000010),
        "default": ModelConfig("groq", "llama-3.3-70b-versatile", 0.00000059, 0.00000079),
    },
    "openai": {
        "fast": ModelConfig("openai", "gpt-4o-mini", 0.00000015, 0.00000060),
        "default": ModelConfig("openai", "gpt-4o", 0.00000250, 0.00001000),
    },
    "nvidia": {
        # meta/llama-3.1-8b-instruct measured ~10s/call (vs 78-188s for
        # nemotron-super-49b) on this free-tier account; fast fallback when
        # Groq's 100k TPD window is exhausted. Quality is lower, so the rubric
        # retry loop may re-run the writer — still ~2-4x faster end to end.
        "fast": ModelConfig("nvidia", "meta/llama-3.1-8b-instruct", 0.0, 0.0),
        "default": ModelConfig("nvidia", "meta/llama-3.1-8b-instruct", 0.0, 0.0),
    },
    "ollama": {
        "default": ModelConfig("ollama", "llama3.1:8b", 0.0, 0.0),
    },
}

TASK_MODEL_MAP: dict[TaskComplexity, list[tuple[str, str]]] = {
    "simple": [("groq", "fast"), ("openai", "fast"), ("nvidia", "fast"), ("ollama", "default"), ("groq", "default")],
    "medium": [("groq", "default"), ("groq", "fast"), ("openai", "fast"), ("nvidia", "default"), ("ollama", "default")],
    "complex": [("groq", "default"), ("groq", "fast"), ("openai", "default"), ("nvidia", "default"), ("ollama", "default")],
}
