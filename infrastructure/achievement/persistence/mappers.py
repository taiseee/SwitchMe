"""AchievementRecord マッパー"""

from domain.achievement.models import (
    AchievementRecord,
    AchievementStatus,
    Evidence,
)
from infrastructure.shared.models import AchievementRecordModel


def achievement_to_orm(achievement: AchievementRecord) -> AchievementRecordModel:
    """ドメインモデル → ORMモデル

    Args:
        achievement: 達成記録ドメインモデル

    Returns:
        達成記録ORMモデル
    """
    # UUIDをリストに変換（JSONシリアライズ用）
    references_list = [str(ref) for ref in achievement.evidence.references]

    return AchievementRecordModel(
        id=achievement.id,
        milestone_id=achievement.milestone_id,
        user_id=achievement.user_id,
        # AchievementStatus → 3カラム
        status_achieved=achievement.status.achieved,
        status_score=achievement.status.score,
        status_reason=achievement.status.reason,
        # Evidence → 3カラム
        evidence_type=achievement.evidence.type,
        evidence_references=references_list,
        evidence_metadata=achievement.evidence.metadata,
        recorded_at=achievement.recorded_at,
    )


def orm_to_achievement(model: AchievementRecordModel) -> AchievementRecord:
    """ORMモデル → ドメインモデル

    Args:
        model: 達成記録ORMモデル

    Returns:
        達成記録ドメインモデル
    """
    from uuid import UUID

    # 文字列リストをUUIDリストに変換
    references_list = [UUID(ref) for ref in model.evidence_references]

    return AchievementRecord(
        id=model.id,
        milestone_id=model.milestone_id,
        user_id=model.user_id,
        status=AchievementStatus(
            achieved=model.status_achieved,
            score=model.status_score,
            reason=model.status_reason,
        ),
        evidence=Evidence(
            type=model.evidence_type,
            references=references_list,
            metadata=model.evidence_metadata,
        ),
        recorded_at=model.recorded_at,
    )
