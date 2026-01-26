"""Milestoneユースケースのテスト"""

from unittest.mock import AsyncMock, Mock
from datetime import date, time
from uuid import uuid4

import pytest

from application.milestone.use_cases import (
    CreateMilestoneInput,
    CreateMilestoneUseCase,
    UpdateMilestoneInput,
    UpdateMilestoneUseCase,
    GetMilestonesUseCase,
    DeleteMilestoneUseCase,
)
from domain.milestone.models import Milestone, Title
from domain.milestone.repositories import MilestoneRepository
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.exceptions import UnauthorizedError
from domain.shared.value_objects import Money
from domain.user.models import UserId
from infrastructure.shared.result import Ok


@pytest.fixture
def repository():
    """テスト用のマイルストーンリポジトリ"""
    repo = Mock(spec=MilestoneRepository)
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_user_id = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def user_id():
    """テスト用のユーザーID"""
    return UserId(value=uuid4())


class TestCreateMilestoneUseCase:
    """CreateMilestoneUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_マイルストーン作成が成功すること(self, repository, user_id):
        """マイルストーン作成が成功すること"""
        repository.save.return_value = Ok(None)
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

        result = await use_case.execute(input_data)

        assert result.is_ok()
        milestone = result.unwrap()
        assert milestone.title.value == "朝のジムトレーニング"
        assert milestone.user_id == user_id
        assert milestone.status == "active"
        assert milestone.penalty.amount.amount == 1000
        repository.save.assert_awaited_once()
        saved_milestone = repository.save.await_args.args[0]
        assert saved_milestone == milestone


class TestUpdateMilestoneUseCase:
    """UpdateMilestoneUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_マイルストーン更新が成功すること(self, repository, user_id):
        """マイルストーン更新が成功すること"""
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
        repository.find_by_id.return_value = Ok(milestone)
        repository.save.return_value = Ok(None)

        use_case = UpdateMilestoneUseCase(milestone_repository=repository)

        input_data = UpdateMilestoneInput(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),
            title="朝のランニング",
        )

        result = await use_case.execute(input_data)

        assert result.is_ok()
        updated_milestone = result.unwrap()
        assert updated_milestone.title.value == "朝のランニング"
        repository.find_by_id.assert_awaited_once_with(milestone.id)
        repository.save.assert_awaited_once()
        saved_milestone = repository.save.await_args.args[0]
        assert saved_milestone.title.value == "朝のランニング"

    @pytest.mark.anyio
    async def test_他のユーザーのマイルストーン更新は失敗すること(
        self, repository, user_id
    ):
        """他のユーザーのマイルストーン更新は失敗すること（認可チェック）"""
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
        repository.find_by_id.return_value = Ok(milestone)

        use_case = UpdateMilestoneUseCase(milestone_repository=repository)

        input_data = UpdateMilestoneInput(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),
            title="不正な更新",
        )

        result = await use_case.execute(input_data)
        assert result.is_err()
        assert isinstance(result.unwrap_err(), UnauthorizedError)
        repository.find_by_id.assert_awaited_once_with(milestone.id)
        repository.save.assert_not_awaited()


class TestGetMilestonesUseCase:
    """GetMilestonesUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_ユーザーのマイルストーン一覧を取得できること(
        self, repository, user_id
    ):
        """ユーザーのマイルストーン一覧を取得できること"""
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
        repository.find_by_user_id.return_value = Ok([milestone1, milestone2])

        use_case = GetMilestonesUseCase(milestone_repository=repository)
        result = await use_case.execute(str(user_id.value))

        assert result.is_ok()
        milestones = result.unwrap()
        assert len(milestones) == 2
        repository.find_by_user_id.assert_awaited_once_with(user_id)


class TestDeleteMilestoneUseCase:
    """DeleteMilestoneUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_マイルストーン削除が成功すること(self, repository, user_id):
        """マイルストーン削除が成功すること"""
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
        repository.find_by_id.return_value = Ok(milestone)
        repository.delete.return_value = Ok(None)

        use_case = DeleteMilestoneUseCase(milestone_repository=repository)
        result = await use_case.execute(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),
        )

        assert result.is_ok()
        repository.find_by_id.assert_awaited_once_with(milestone.id)
        repository.delete.assert_awaited_once_with(milestone.id)

    @pytest.mark.anyio
    async def test_他のユーザーのマイルストーン削除は失敗すること(
        self, repository, user_id
    ):
        """他のユーザーのマイルストーン削除は失敗すること（認可チェック）"""
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
        repository.find_by_id.return_value = Ok(milestone)

        use_case = DeleteMilestoneUseCase(milestone_repository=repository)
        result = await use_case.execute(
            milestone_id=str(milestone.id.value),
            user_id=str(user_id.value),
        )

        assert result.is_err()
        assert isinstance(result.unwrap_err(), UnauthorizedError)
        repository.find_by_id.assert_awaited_once_with(milestone.id)
        repository.delete.assert_not_awaited()
