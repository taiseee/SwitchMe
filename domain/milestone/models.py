"""Milestoneドメインモデル"""

from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.value_objects import Money
from domain.user.models import UserId


class MilestoneId(BaseModel):
    """マイルストーンID（値オブジェクト）"""

    model_config = {"frozen": True}

    value: UUID = Field(...)


class Title(BaseModel):
    """マイルストーンタイトル（値オブジェクト）"""

    model_config = {"frozen": True}

    value: str = Field(..., min_length=1, description="タイトル")

    @field_validator("value")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """タイトルの検証"""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v


MilestoneStatus = Literal["active", "completed", "failed", "cancelled"]


class Milestone(BaseModel):
    """マイルストーン（集約ルート）

    ユーザーが設定した目標・習慣を表現する。
    不変（frozen）で、変更は新しいインスタンスを返すメソッドで行う。
    """

    model_config = {"frozen": True}

    id: MilestoneId
    user_id: UserId
    title: Title
    deadline: DeadlineInfo
    verification_criteria: VerificationCriteria
    penalty: PenaltyInfo
    status: MilestoneStatus = Field(default="active")

    @classmethod
    def create(
        cls,
        user_id: UserId,
        title: Title,
        deadline: DeadlineInfo,
        verification_criteria: VerificationCriteria,
        penalty: PenaltyInfo,
    ) -> "Milestone":
        """新しいマイルストーンを作成する

        Args:
            user_id: ユーザーID
            title: タイトル
            deadline: 期限情報
            verification_criteria: 検証基準
            penalty: ペナルティ情報

        Returns:
            作成されたマイルストーン
        """
        return cls(
            id=MilestoneId(value=uuid4()),
            user_id=user_id,
            title=title,
            deadline=deadline,
            verification_criteria=verification_criteria,
            penalty=penalty,
            status="active",
        )

    def update(
        self,
        title: Title | None = None,
        deadline: DeadlineInfo | None = None,
        verification_criteria: VerificationCriteria | None = None,
    ) -> "Milestone":
        """マイルストーンを更新する

        Args:
            title: 新しいタイトル（Noneの場合は変更しない）
            deadline: 新しい期限情報（Noneの場合は変更しない）
            verification_criteria: 新しい検証基準（Noneの場合は変更しない）

        Returns:
            更新されたマイルストーン
        """
        updates = {}
        if title is not None:
            updates["title"] = title
        if deadline is not None:
            updates["deadline"] = deadline
        if verification_criteria is not None:
            updates["verification_criteria"] = verification_criteria

        return self.model_copy(update=updates)

    def set_penalty_amount(self, amount: Money) -> "Milestone":
        """ペナルティ金額を変更する

        Args:
            amount: 新しいペナルティ金額

        Returns:
            ペナルティ金額が変更されたマイルストーン
        """
        new_penalty = PenaltyInfo(
            amount=amount,
            description=self.penalty.description,
        )
        return self.model_copy(update={"penalty": new_penalty})

    def complete(self) -> "Milestone":
        """マイルストーンを完了にする

        Returns:
            ステータスがcompletedに変更されたマイルストーン
        """
        return self.model_copy(update={"status": "completed"})

    def fail(self) -> "Milestone":
        """マイルストーンを失敗にする

        Returns:
            ステータスがfailedに変更されたマイルストーン
        """
        return self.model_copy(update={"status": "failed"})

    def cancel(self) -> "Milestone":
        """マイルストーンをキャンセルする

        Returns:
            ステータスがcancelledに変更されたマイルストーン
        """
        return self.model_copy(update={"status": "cancelled"})
