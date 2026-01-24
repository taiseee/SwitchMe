"""Milestoneユースケース"""

from datetime import date, time
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field
from domain.milestone.models import Milestone, MilestoneId, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.milestone.repositories import MilestoneRepository
from domain.shared.value_objects import Money
from domain.user.models import UserId
from domain.shared.exceptions import UnauthorizedError
from infrastructure.shared.result import Result, Ok, Err


class CreateMilestoneInput(BaseModel):
    """マイルストーン作成の入力モデル"""

    user_id: str = Field(..., description="ユーザーID")
    title: str = Field(..., min_length=1, description="タイトル")
    deadline_date: str = Field(..., description="期限日（YYYY-MM-DD）")
    deadline_time: str = Field(..., description="期限時刻（HH:MM:SS）")
    timezone: str = Field(..., description="タイムゾーン")
    verification_type: str = Field(..., description="検証タイプ")
    verification_conditions: dict[str, Any] = Field(..., description="検証条件")
    verification_threshold: float = Field(..., description="検証閾値")
    penalty_amount: int = Field(..., ge=0, description="ペナルティ金額")
    penalty_currency: str = Field(..., description="通貨コード")
    penalty_description: str = Field(default="", description="ペナルティの説明")


class UpdateMilestoneInput(BaseModel):
    """マイルストーン更新の入力モデル"""

    milestone_id: str = Field(..., description="マイルストーンID")
    user_id: str = Field(..., description="ユーザーID（認可用）")
    title: str | None = Field(default=None, description="タイトル")
    deadline_date: str | None = Field(default=None, description="期限日（YYYY-MM-DD）")
    deadline_time: str | None = Field(default=None, description="期限時刻（HH:MM:SS）")
    timezone: str | None = Field(default=None, description="タイムゾーン")


class CreateMilestoneUseCase:
    """マイルストーン作成ユースケース"""

    def __init__(self, milestone_repository: MilestoneRepository) -> None:
        self._milestone_repository = milestone_repository

    def execute(self, input_data: CreateMilestoneInput) -> Result[Milestone, Exception]:
        """マイルストーン作成を実行する

        Args:
            input_data: 作成情報

        Returns:
            成功時はOk(Milestone)、失敗時はErr(Exception)
        """
        # 値オブジェクトの作成
        user_id = UserId(value=UUID(input_data.user_id))
        title = Title(value=input_data.title)
        deadline = DeadlineInfo(
            date=date.fromisoformat(input_data.deadline_date),
            time=time.fromisoformat(input_data.deadline_time),
            timezone=input_data.timezone,
        )
        verification_criteria = VerificationCriteria(
            type=input_data.verification_type,  # type: ignore
            conditions=input_data.verification_conditions,
            threshold=input_data.verification_threshold,
        )
        penalty = PenaltyInfo(
            amount=Money(
                amount=input_data.penalty_amount,
                currency=input_data.penalty_currency,  # type: ignore
            ),
            description=input_data.penalty_description,
        )

        # マイルストーン作成
        milestone = Milestone.create(
            user_id=user_id,
            title=title,
            deadline=deadline,
            verification_criteria=verification_criteria,
            penalty=penalty,
        )

        # 保存
        save_result = self._milestone_repository.save(milestone)
        if save_result.is_err():
            return Err(Exception("Failed to save milestone"))

        return Ok(milestone)


class UpdateMilestoneUseCase:
    """マイルストーン更新ユースケース"""

    def __init__(self, milestone_repository: MilestoneRepository) -> None:
        self._milestone_repository = milestone_repository

    def execute(self, input_data: UpdateMilestoneInput) -> Result[Milestone, Exception]:
        """マイルストーン更新を実行する

        Args:
            input_data: 更新情報

        Returns:
            成功時はOk(Milestone)、失敗時はErr(Exception)
        """
        # マイルストーンを取得
        milestone_id = MilestoneId(value=UUID(input_data.milestone_id))
        found_result = self._milestone_repository.find_by_id(milestone_id)
        if found_result.is_err():
            return Err(Exception("Milestone not found"))

        milestone = found_result.unwrap()

        # 認可チェック（所有者のみ更新可能）
        user_id = UserId(value=UUID(input_data.user_id))
        if milestone.user_id.value != user_id.value:
            return Err(
                UnauthorizedError("You are not authorized to update this milestone")
            )

        # 更新
        title = Title(value=input_data.title) if input_data.title else None
        deadline = None
        if input_data.deadline_date and input_data.deadline_time:
            deadline = DeadlineInfo(
                date=date.fromisoformat(input_data.deadline_date),
                time=time.fromisoformat(input_data.deadline_time),
                timezone=input_data.timezone or milestone.deadline.timezone,
            )

        updated_milestone = milestone.update(title=title, deadline=deadline)

        # 保存
        save_result = self._milestone_repository.save(updated_milestone)
        if save_result.is_err():
            return Err(Exception("Failed to save milestone"))

        return Ok(updated_milestone)


class GetMilestonesUseCase:
    """マイルストーン一覧取得ユースケース"""

    def __init__(self, milestone_repository: MilestoneRepository) -> None:
        self._milestone_repository = milestone_repository

    def execute(self, user_id: str) -> Result[list[Milestone], Exception]:
        """ユーザーのマイルストーン一覧を取得する

        Args:
            user_id: ユーザーID

        Returns:
            成功時はOk(list[Milestone])、失敗時はErr(Exception)
        """
        user_id_obj = UserId(value=UUID(user_id))
        return self._milestone_repository.find_by_user_id(user_id_obj)


class DeleteMilestoneUseCase:
    """マイルストーン削除ユースケース"""

    def __init__(self, milestone_repository: MilestoneRepository) -> None:
        self._milestone_repository = milestone_repository

    def execute(self, milestone_id: str, user_id: str) -> Result[None, Exception]:
        """マイルストーンを削除する

        Args:
            milestone_id: マイルストーンID
            user_id: ユーザーID（認可用）

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        # マイルストーンを取得
        milestone_id_obj = MilestoneId(value=UUID(milestone_id))
        found_result = self._milestone_repository.find_by_id(milestone_id_obj)
        if found_result.is_err():
            return Err(Exception("Milestone not found"))

        milestone = found_result.unwrap()

        # 認可チェック（所有者のみ削除可能）
        user_id_obj = UserId(value=UUID(user_id))
        if milestone.user_id.value != user_id_obj.value:
            return Err(
                UnauthorizedError("You are not authorized to delete this milestone")
            )

        # 削除
        return self._milestone_repository.delete(milestone_id_obj)
