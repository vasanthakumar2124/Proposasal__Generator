from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from app.domain.exceptions import ValidationError


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")
        if not self.currency:
            raise ValidationError("Currency cannot be empty")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValidationError(f"Cannot add different currencies: {self.currency} vs {other.currency}")
        return Money(amount=(self.amount + other.amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), currency=self.currency)

    def __mul__(self, multiplier: int | float) -> "Money":
        return Money(amount=(self.amount * Decimal(str(multiplier))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), currency=self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"

    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        return cls(amount=Decimal("0.00"), currency=currency)
