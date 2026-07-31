import re
from dataclasses import dataclass
from app.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Email:
    address: str

    def __post_init__(self) -> None:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.address):
            raise ValidationError(f"Invalid email address: {self.address}")

    def __str__(self) -> str:
        return self.address
