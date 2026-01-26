"""達成記録ドメインモデル"""

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Any


class AchievementStatus(BaseModel):
    """達成状態（値オブジェクト）

    マイルストーンの達成/未達成状態を表現する。
    """

    model_config = {"frozen": True}

    achieved: bool = Field(..., description="達成フラグ")
    score: float = Field(..., ge=0, le=1, description="達成スコア（0〜1）")
    reason: str = Field(default="", description="達成/未達成の理由")


class Evidence(BaseModel):
    """証拠（値オブジェクト）

    達成記録の証拠となる情報を保持する。
    """

    model_config = {"frozen": True}

    type: str = Field(..., description="証拠タイプ（verification, manual, etc.）")
    references: list[UUID] = Field(
        default_factory=list, description="参照ID（検証IDなど）"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="追加メタデータ")


class AchievementRecord(BaseModel):
    """達成記録（集約ルート）

    マイルストーンの達成/未達成を記録する。
    """

    model_config = {"frozen": True}

    id: UUID = Field(..., description="達成記録ID")
    milestone_id: UUID = Field(..., description="マイルストーンID")
    user_id: UUID = Field(..., description="ユーザーID")
    status: AchievementStatus = Field(..., description="達成状態")
    evidence: Evidence = Field(..., description="証拠")
    recorded_at: datetime = Field(..., description="記録日時")

    @classmethod
    def record_achievement(
        cls,
        milestone_id: UUID,
        user_id: UUID,
        verification_id: UUID,
        score: float,
    ) -> "AchievementRecord":
        """達成を記録する

        Args:
            milestone_id: マイルストーンID
            user_id: ユーザーID
            verification_id: 検証ID
            score: 達成スコア

        Returns:
            新しいAchievementRecordインスタンス（達成）
        """
        return cls(
            id=uuid4(),
            milestone_id=milestone_id,
            user_id=user_id,
            status=AchievementStatus(
                achieved=True, score=score, reason="Verified by GPS"
            ),
            evidence=Evidence(type="verification", references=[verification_id]),
            recorded_at=datetime.now(timezone.utc),
        )

    @classmethod
    def record_failure(
        cls, milestone_id: UUID, user_id: UUID, reason: str
    ) -> "AchievementRecord":
        """未達成を記録する

        Args:
            milestone_id: マイルストーンID
            user_id: ユーザーID
            reason: 未達成の理由

        Returns:
            新しいAchievementRecordインスタンス（未達成）
        """
        return cls(
            id=uuid4(),
            milestone_id=milestone_id,
            user_id=user_id,
            status=AchievementStatus(achieved=False, score=0.0, reason=reason),
            evidence=Evidence(type="manual", metadata={"reason": reason}),
            recorded_at=datetime.now(timezone.utc),
        )
