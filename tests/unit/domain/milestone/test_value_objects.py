"""Milestone値オブジェクトのテスト"""

from datetime import datetime, date, time
import pytest
from pydantic import ValidationError
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.value_objects import Money


class TestDeadlineInfo:
    """DeadlineInfoのテスト"""

    def test_期限情報が作成できること(self):
        """期限情報が作成できること"""
        deadline = DeadlineInfo(
            date=date(2026, 1, 31),
            time=time(18, 0, 0),
            timezone="Asia/Tokyo",
        )
        assert deadline.deadline_date == date(2026, 1, 31)
        assert deadline.deadline_time == time(18, 0, 0)
        assert deadline.timezone == "Asia/Tokyo"

    def test_期限情報は不変であること(self):
        """DeadlineInfoは不変（frozen）であること"""
        deadline = DeadlineInfo(
            date=date(2026, 1, 31),
            time=time(18, 0, 0),
            timezone="Asia/Tokyo",
        )
        with pytest.raises((ValidationError, AttributeError)):
            deadline.deadline_date = date(2026, 2, 1)  # type: ignore

    def test_datetimeに変換できること(self):
        """to_datetime()でdatetimeに変換できること"""
        deadline = DeadlineInfo(
            date=date(2026, 1, 31),
            time=time(18, 0, 0),
            timezone="Asia/Tokyo",
        )
        dt = deadline.to_datetime()
        assert isinstance(dt, datetime)
        assert dt.date() == date(2026, 1, 31)
        assert dt.time() == time(18, 0, 0)


class TestVerificationCriteria:
    """VerificationCriteriaのテスト"""

    def test_位置情報検証基準が作成できること(self):
        """位置情報検証基準が作成できること"""
        criteria = VerificationCriteria(
            type="location",
            conditions={"latitude": 35.6812, "longitude": 139.7671},
            threshold=100.0,
        )
        assert criteria.type == "location"
        assert criteria.conditions["latitude"] == 35.6812
        assert criteria.threshold == 100.0

    def test_画像検証基準が作成できること(self):
        """画像検証基準が作成できること"""
        criteria = VerificationCriteria(
            type="image",
            conditions={"required_objects": ["desk", "laptop"]},
            threshold=0.8,
        )
        assert criteria.type == "image"
        assert criteria.conditions["required_objects"] == ["desk", "laptop"]

    def test_不正な検証タイプは拒否されること(self):
        """不正な検証タイプは拒否されること"""
        with pytest.raises(ValidationError):
            VerificationCriteria(
                type="invalid",  # type: ignore
                conditions={},
                threshold=1.0,
            )

    def test_検証基準は不変であること(self):
        """VerificationCriteriaは不変（frozen）であること"""
        criteria = VerificationCriteria(
            type="location",
            conditions={},
            threshold=100.0,
        )
        with pytest.raises((ValidationError, AttributeError)):
            criteria.type = "image"  # type: ignore


class TestPenaltyInfo:
    """PenaltyInfoのテスト"""

    def test_ペナルティ情報が作成できること(self):
        """ペナルティ情報が作成できること"""
        penalty = PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="朝のジム未達成",
        )
        assert penalty.amount.amount == 1000
        assert penalty.amount.currency == "JPY"
        assert penalty.description == "朝のジム未達成"

    def test_説明なしでペナルティ情報が作成できること(self):
        """説明なしでペナルティ情報が作成できること"""
        penalty = PenaltyInfo(
            amount=Money(amount=500, currency="USD"),
            description="",
        )
        assert penalty.amount.amount == 500
        assert penalty.description == ""

    def test_ペナルティ情報は不変であること(self):
        """PenaltyInfoは不変（frozen）であること"""
        penalty = PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="テスト",
        )
        with pytest.raises((ValidationError, AttributeError)):
            penalty.amount = Money(amount=2000, currency="JPY")  # type: ignore
