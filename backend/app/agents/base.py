import logging
from abc import ABC, abstractmethod
from typing import Any

from app.llm import LLMClient, LLMResponse

logger = logging.getLogger("proposalcraft.agents")


class BaseAgent(ABC):
    name: str = "base"

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    @abstractmethod
    def run(self, state: dict) -> dict:
        ...

    def _llm_call(self, prompt: str, **kwargs) -> LLMResponse:
        return self.llm.generate(prompt, **kwargs)

    def _llm_json(self, prompt: str, **kwargs) -> dict:
        return self.llm.generate_json(prompt, **kwargs)
