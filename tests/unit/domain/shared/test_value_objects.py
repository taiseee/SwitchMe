"""共通値オブジェクトのテスト"""

import pytest
from pydantic import ValidationError
from domain.shared.value_objects import Money


class TestMoney:
    """Moneyのテスト"""

    def test_正の金額でmoneyが作成できること(self):
        """正の金額でMoneyが作成できること"""
        money = Money(amount=1000, currency="JPY")
        assert money.amount == 1000
        assert money.currency == "JPY"

    def test_ゼロ金額でmoneyが作成できること(self):
        """ゼロ金額でMoneyが作成できること"""
        money = Money(amount=0, currency="USD")
        assert money.amount == 0
        assert money.currency == "USD"

    def test_負の金額は拒否されること(self):
        """負の金額は拒否されること"""
        with pytest.raises(ValidationError) as exc_info:
            Money(amount=-100, currency="JPY")
        errors = exc_info.value.errors()
        assert any("greater than or equal to 0" in str(error) for error in errors)

    def test_不正な通貨は拒否されること(self):
        """不正な通貨コードは拒否されること"""
        with pytest.raises(ValidationError):
            Money(amount=1000, currency="INVALID")

    def test_同じ通貨のmoneyを加算できること(self):
        """同じ通貨のMoneyを加算できること"""
        money1 = Money(amount=1000, currency="JPY")
        money2 = Money(amount=500, currency="JPY")
        result = money1.add(money2)
        assert result.amount == 1500
        assert result.currency == "JPY"

    def test_異なる通貨のmoneyは加算できないこと(self):
        """異なる通貨のMoneyは加算できないこと"""
        money1 = Money(amount=1000, currency="JPY")
        money2 = Money(amount=500, currency="USD")
        with pytest.raises(ValueError, match="Cannot add different currencies"):
            money1.add(money2)

    def test_moneyは不変であること(self):
        """Moneyは不変（frozen）であること"""
        money = Money(amount=1000, currency="JPY")
        with pytest.raises((ValidationError, AttributeError)):
            money.amount = 2000  # type: ignore

    def test_同じ値のmoneyは等価であること(self):
        """同じ値のMoneyは等価であること"""
        money1 = Money(amount=1000, currency="JPY")
        money2 = Money(amount=1000, currency="JPY")
        assert money1 == money2

    def test_異なる値のmoneyは等価でないこと(self):
        """異なる値のMoneyは等価でないこと"""
        money1 = Money(amount=1000, currency="JPY")
        money2 = Money(amount=2000, currency="JPY")
        assert money1 != money2

    def test_対応通貨コードが正しいこと(self):
        """対応している通貨コード（JPY, USD, EUR）が正しいこと"""
        Money(amount=100, currency="JPY")
        Money(amount=100, currency="USD")
        Money(amount=100, currency="EUR")
