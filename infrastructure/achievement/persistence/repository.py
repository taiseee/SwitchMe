"""PostgreSQL Achievement Repository実装"""

from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from domain.achievement.models import AchievementRecord
from infrastructure.shared.models import AchievementRecordModel
from infrastructure.shared.result import Result, Ok, Err
from domain.shared.exceptions import EntityNotFoundError
from infrastructure.achievement.persistence.mappers import (
    achievement_to_orm,
    orm_to_achievement,
)


class PostgresAchievementRepository:
    """PostgreSQL Achievement Repository実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, achievement: AchievementRecord) -> Result[None, Exception]:
        """達成記録を保存（INSERT or UPDATE）

        Args:
            achievement: 達成記録エンティティ

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        try:
            achievement_model = achievement_to_orm(achievement)

            # 既存チェック
            stmt = select(AchievementRecordModel).where(
                AchievementRecordModel.id == achievement_model.id
            )
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # UPDATE
                existing.status_achieved = achievement_model.status_achieved
                existing.status_score = achievement_model.status_score
                existing.status_reason = achievement_model.status_reason
                existing.evidence_type = achievement_model.evidence_type
                existing.evidence_references = achievement_model.evidence_references
                existing.evidence_metadata = achievement_model.evidence_metadata
                existing.recorded_at = achievement_model.recorded_at
                existing.updated_at = datetime.now(UTC)
            else:
                # INSERT
                self._session.add(achievement_model)

            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)

    async def find_by_id(
        self, achievement_id: UUID
    ) -> Result[AchievementRecord, EntityNotFoundError]:
        """IDで達成記録を検索

        Args:
            achievement_id: 達成記録ID

        Returns:
            成功: Ok(AchievementRecord)
            失敗: Err(EntityNotFoundError)
        """
        stmt = select(AchievementRecordModel).where(
            AchievementRecordModel.id == achievement_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Err(EntityNotFoundError("AchievementRecord", str(achievement_id)))

        return Ok(orm_to_achievement(model))

    async def find_by_milestone_id(
        self, milestone_id: UUID
    ) -> Result[list[AchievementRecord], Exception]:
        """マイルストーンIDで達成記録を検索

        Args:
            milestone_id: マイルストーンID

        Returns:
            成功: Ok(list[AchievementRecord])
            失敗: Err(Exception)
        """
        try:
            stmt = select(AchievementRecordModel).where(
                AchievementRecordModel.milestone_id == milestone_id
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()

            achievements = [orm_to_achievement(model) for model in models]
            return Ok(achievements)
        except Exception as e:
            return Err(e)

    async def find_by_user_id(
        self, user_id: UUID
    ) -> Result[list[AchievementRecord], Exception]:
        """ユーザーIDで達成記録を検索

        Args:
            user_id: ユーザーID

        Returns:
            成功: Ok(list[AchievementRecord])
            失敗: Err(Exception)
        """
        try:
            stmt = select(AchievementRecordModel).where(
                AchievementRecordModel.user_id == user_id
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()

            achievements = [orm_to_achievement(model) for model in models]
            return Ok(achievements)
        except Exception as e:
            return Err(e)

    async def delete(self, achievement_id: UUID) -> Result[None, Exception]:
        """達成記録を削除

        Args:
            achievement_id: 達成記録ID

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        try:
            stmt = sql_delete(AchievementRecordModel).where(
                AchievementRecordModel.id == achievement_id
            )
            await self._session.execute(stmt)
            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)
