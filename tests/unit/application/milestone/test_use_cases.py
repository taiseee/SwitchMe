"""Milestoneユースケースのテスト"""

from datetime import date, time
from uuid import uuid4
import pytest
from domain.milestone.models import Milestone, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.milestone.repositories import InMemoryMilestoneRepository
from domain.shared.value_objects import Money
from domain.user.models import UserId
from application.milestone.use_cases import (
    CreateMilestoneInput,
    CreateMilestoneUseCase,
    UpdateMilestoneInput,
    UpdateMilestoneUseCase,
    GetMilestonesUseCase,
    DeleteMilestoneUseCase,
)


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryMilestoneRepository()


@pytest.fixture
def user_id():
    """テスト用のユーザーID"""
    return UserId(value=uuid4())


class TestCreateMilestoneUseCase:
    """CreateMilestoneUseCaseのテスト"""

    def test_マイルストーン作成が成功すること(self, repository, user_id):
        """マイルストーン作成が成功すること"""
        use_case = CreateMilestoneUseCase(milestone_repository=repository)

        input_data = CreateMilestoneInput(
            user_id=str(user_id.value),
            title="朝のジムトレーニング",
            deadline_date="2026-01-31",
            deadline_time="18:00:00",
            timezone="Asia/Tokyo",
            verification_type="location",
            verification_conditions={"latitude": 35.6812, "longitude": 139.7671},
            verification_threshold=100.0,
            penalty_amount=1000,
            penalty_currency="JPY",
            penalty_description="朝のジム未達成",
        )

        result = use_case.execute(input_data)

        assert result.is_ok()
        milestone = result.unwrap()
        assert milestone.title.value == "朝のジムトレーニング"
        assert milestone.user_id == user_id
        assert milestone.status == "active"
        assert milestone.penalty.amount.amount == 1000

        # リポジトリに保存されていることを確認
        found_result = repository.find_by_id(milestone.id)
        assert found_result.is_ok()


class TestUpdateMilestoneUseCase:
    """UpdateMilestoneUseCaseのテスト"""

    def test_マイルストーン更新が成功すること(self, repository, user_id):
        """マイルストーン更新が成功すること"""
        # 既存のマイルストーンを作成
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
        repository.save(milestone)

        # 更新ユースケース
        use_case = UpdateMilestoneUseCase(milestone_repository=repository)

        input_data = UpdateMilestoneInput(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),
            title="朝のランニング",
        )

        result = use_case.execute(input_data)

        assert result.is_ok()
        updated_milestone = result.unwrap()
        assert updated_milestone.title.value == "朝のランニング"

    def test_他のユーザーのマイルストーン更新は失敗すること(self, repository, user_id):
        """他のユーザーのマイルストーン更新は失敗すること（認可チェック）"""
        # 別のユーザーのマイルストーンを作成
        other_user_id = UserId(value=uuid4())
        milestone = Milestone.create(
            user_id=other_user_id,
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
        repository.save(milestone)

        # 別のユーザーで更新を試みる
        use_case = UpdateMilestoneUseCase(milestone_repository=repository)

        input_data = UpdateMilestoneInput(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),  # 異なるユーザーID
            title="不正な更新",
        )

        result = use_case.execute(input_data)
        assert result.is_err()


class TestGetMilestonesUseCase:
    """GetMilestonesUseCaseのテスト"""

    def test_ユーザーのマイルストーン一覧を取得できること(self, repository, user_id):
        """ユーザーのマイルストーン一覧を取得できること"""
        # 複数のマイルストーンを作成
        milestone1 = Milestone.create(
            user_id=user_id,
            title=Title(value="朝のジム"),
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
        milestone2 = Milestone.create(
            user_id=user_id,
            title=Title(value="夜のランニング"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 31),
                time=time(20, 0, 0),
                timezone="Asia/Tokyo",
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=500, currency="JPY"),
                description="",
            ),
        )
        repository.save(milestone1)
        repository.save(milestone2)

        # 一覧取得
        use_case = GetMilestonesUseCase(milestone_repository=repository)
        result = use_case.execute(str(user_id.value))

        assert result.is_ok()
        milestones = result.unwrap()
        assert len(milestones) == 2


class TestDeleteMilestoneUseCase:
    """DeleteMilestoneUseCaseのテスト"""

    def test_マイルストーン削除が成功すること(self, repository, user_id):
        """マイルストーン削除が成功すること"""
        # マイルストーンを作成
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
        repository.save(milestone)

        # 削除
        use_case = DeleteMilestoneUseCase(milestone_repository=repository)
        result = use_case.execute(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),
        )

        assert result.is_ok()

        # 削除後は取得できない
        found_result = repository.find_by_id(milestone.id)
        assert found_result.is_err()

    def test_他のユーザーのマイルストーン削除は失敗すること(self, repository, user_id):
        """他のユーザーのマイルストーン削除は失敗すること（認可チェック）"""
        # 別のユーザーのマイルストーンを作成
        other_user_id = UserId(value=uuid4())
        milestone = Milestone.create(
            user_id=other_user_id,
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
        repository.save(milestone)

        # 別のユーザーで削除を試みる
        use_case = DeleteMilestoneUseCase(milestone_repository=repository)
        result = use_case.execute(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),  # 異なるユーザーID
        )

        assert result.is_err()
