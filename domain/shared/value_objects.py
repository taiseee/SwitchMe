"""共通値オブジェクト"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


CurrencyCode = Literal["JPY", "USD", "EUR"]


class Money(BaseModel):
    """金額を表す値オブジェクト

    不変（frozen）で、値に基づく同一性を持つ。
    """

    model_config = {"frozen": True}

    amount: int = Field(..., ge=0, description="金額（0以上）")
    currency: CurrencyCode = Field(..., description="通貨コード")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """通貨コードの検証"""
        allowed = ["JPY", "USD", "EUR"]
        if v not in allowed:
            raise ValueError(f"Currency must be one of {allowed}, got {v}")
        return v

    def add(self, other: "Money") -> "Money":
        """同じ通貨のMoneyを加算する

        Args:
            other: 加算するMoney

        Returns:
            加算結果の新しいMoney

        Raises:
            ValueError: 異なる通貨のMoneyを加算しようとした場合
        """
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(amount=self.amount + other.amount, currency=self.currency)
