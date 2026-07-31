from abc import ABC, abstractmethod
from typing import Any


class BaseEngine(ABC):
    """All business engines inherit from this.
    Engines are pure Python — NO LLM calls.
    """

    name: str = "base"

    @abstractmethod
    def run(self, context: dict) -> dict:
        pass

    def validate_input(self, context: dict, required_keys: list[str]) -> None:
        missing = [k for k in required_keys if k not in context]
        if missing:
            raise ValueError(f"Engine '{self.name}' missing required keys: {missing}")
