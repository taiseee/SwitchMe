"""PostgreSQL Milestone Repository implementation"""

from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.milestone.models import Milestone, MilestoneId
from domain.user.models import UserId
from infrastructure.shared.models import MilestoneModel
from infrastructure.milestone.persistence.mappers import (
    milestone_to_orm,
    orm_to_milestone,
)
from infrastructure.shared.result import Ok, Err, Result
from domain.shared.exceptions import EntityNotFoundError


class PostgresMilestoneRepository:
    """PostgreSQL Milestone Repository実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, milestone: Milestone) -> Result[None, Exception]:
        """マイルストーンを保存（INSERT or UPDATE）"""
        try:
            # ドメインモデル → ORMモデル変換
            milestone_model = milestone_to_orm(milestone)

            # 既存チェック
            stmt = select(MilestoneModel).where(MilestoneModel.id == milestone_model.id)
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # UPDATE
                existing.title = milestone_model.title
                existing.deadline_date = milestone_model.deadline_date
                existing.deadline_time = milestone_model.deadline_time
                existing.timezone = milestone_model.timezone
                existing.verification_type = milestone_model.verification_type
                existing.verification_conditions = (
                    milestone_model.verification_conditions
                )
                existing.verification_threshold = milestone_model.verification_threshold
                existing.penalty_amount = milestone_model.penalty_amount
                existing.penalty_currency = milestone_model.penalty_currency
                existing.penalty_description = milestone_model.penalty_description
                existing.status = milestone_model.status
                existing.updated_at = datetime.now(UTC)
            else:
                # INSERT
                self._session.add(milestone_model)

            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)

    async def find_by_id(
        self, milestone_id: MilestoneId
    ) -> Result[Milestone, EntityNotFoundError]:
        """IDでマイルストーンを検索"""
        stmt = select(MilestoneModel).where(MilestoneModel.id == milestone_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Err(EntityNotFoundError("Milestone", str(milestone_id.value)))

        return Ok(orm_to_milestone(model))

    async def find_by_user_id(
        self, user_id: UserId
    ) -> Result[list[Milestone], Exception]:
        """ユーザーIDでマイルストーンを検索"""
        try:
            stmt = select(MilestoneModel).where(MilestoneModel.user_id == user_id.value)
            result = await self._session.execute(stmt)
            models = result.scalars().all()

            milestones = [orm_to_milestone(model) for model in models]
            return Ok(milestones)
        except Exception as e:
            return Err(e)

    async def delete(self, milestone_id: MilestoneId) -> Result[None, Exception]:
        """マイルストーンを削除"""
        try:
            stmt = select(MilestoneModel).where(MilestoneModel.id == milestone_id.value)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return Err(EntityNotFoundError("Milestone", str(milestone_id.value)))

            await self._session.delete(model)
            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)
