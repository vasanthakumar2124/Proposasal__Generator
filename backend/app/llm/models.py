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
    "ollama": {
        "default": ModelConfig("ollama", "llama3.1:8b", 0.0, 0.0),
    },
}

TASK_MODEL_MAP: dict[TaskComplexity, list[tuple[str, str]]] = {
    "simple": [("openai", "fast"), ("groq", "fast"), ("ollama", "default"), ("groq", "default")],
    "medium": [("openai", "fast"), ("groq", "default"), ("groq", "fast"), ("ollama", "default")],
    "complex": [("openai", "default"), ("groq", "default"), ("openai", "fast"), ("groq", "fast")],
}
