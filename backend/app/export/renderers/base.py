import logging
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger("proposalcraft.export")


class BaseRenderer(ABC):
    extension: str = ""

    @abstractmethod
    def render(self, proposal: dict, output_path: str) -> str:
        ...

    def validate_proposal(self, proposal: dict) -> bool:
        return bool(proposal and isinstance(proposal, dict))
