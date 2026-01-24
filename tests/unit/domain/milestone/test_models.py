"""Milestoneドメインモデルのテスト"""

from datetime import date, time
from uuid import UUID
import pytest
from pydantic import ValidationError
from domain.milestone.models import MilestoneId, Title, Milestone
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.value_objects import Money
from domain.user.models import UserId


class TestMilestoneId:
    """MilestoneIdのテスト"""

    def test_uuidで作成できること(self):
        """UUIDでMilestoneIdが作成できること"""
        uuid_value = UUID("12345678-1234-5678-1234-567812345678")
        milestone_id = MilestoneId(value=uuid_value)
        assert milestone_id.value == uuid_value


class TestTitle:
    """Titleのテスト"""

    def test_タイトルが作成できること(self):
        """Titleが作成できること"""
        title = Title(value="朝のジムトレーニング")
        assert title.value == "朝のジムトレーニング"

    def test_空のタイトルは拒否されること(self):
        """空のタイトルは拒否されること"""
        with pytest.raises(ValidationError):
            Title(value="")


class TestMilestone:
    """Milestoneのテスト"""

    def test_milestoneが作成できること(self):
        """Milestoneが作成できること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={"latitude": 35.6812, "longitude": 139.7671},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="朝のジム未達成",
            ),
        )

        assert isinstance(milestone.id, MilestoneId)
        assert milestone.user_id == user_id
        assert milestone.title.value == "朝のジムトレーニング"
        assert milestone.status == "active"
        assert milestone.penalty.amount.amount == 1000

    def test_milestoneを更新できること(self):
        """Milestoneを更新できること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="",
            ),
        )

        # タイトルを更新
        new_title = Title(value="朝のランニング")
        updated_milestone = milestone.update(title=new_title)

        assert updated_milestone.title.value == "朝のランニング"
        assert updated_milestone.id == milestone.id  # IDは変わらない

    def test_ペナルティ金額を設定できること(self):
        """set_penalty_amount()でペナルティ金額を変更できること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="初回ペナルティ",
            ),
        )

        # ペナルティ金額を変更
        new_amount = Money(amount=2000, currency="JPY")
        updated_milestone = milestone.set_penalty_amount(new_amount)

        assert updated_milestone.penalty.amount.amount == 2000

    def test_マイルストーンを完了にできること(self):
        """complete()でステータスをcompletedに変更できること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="",
            ),
        )

        assert milestone.status == "active"
        completed_milestone = milestone.complete()
        assert completed_milestone.status == "completed"

    def test_マイルストーンを失敗にできること(self):
        """fail()でステータスをfailedに変更できること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="",
            ),
        )

        assert milestone.status == "active"
        failed_milestone = milestone.fail()
        assert failed_milestone.status == "failed"

    def test_マイルストーンをキャンセルできること(self):
        """cancel()でステータスをcancelledに変更できること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="",
            ),
        )

        assert milestone.status == "active"
        cancelled_milestone = milestone.cancel()
        assert cancelled_milestone.status == "cancelled"

    def test_milestoneは不変であること(self):
        """Milestoneは不変（frozen）であること"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        milestone = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジムトレーニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(18, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"),
                description="",
            ),
        )

        with pytest.raises((ValidationError, AttributeError)):
            milestone.title = Title(value="新しいタイトル")  # type: ignore
