"""PostgreSQL Verification Repository実装"""

from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.orm import selectinload
from domain.verification.models import Verification
from infrastructure.shared.models import VerificationModel, SensorDataModel
from infrastructure.shared.result import Result, Ok, Err
from domain.shared.exceptions import EntityNotFoundError
from infrastructure.verification.persistence.mappers import (
    verification_to_orm,
    sensor_data_to_orm,
    orm_to_verification,
)


class PostgresVerificationRepository:
    """PostgreSQL Verification Repository実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, verification: Verification) -> Result[None, Exception]:
        """検証を保存（INSERT or UPDATE）

        Args:
            verification: 検証エンティティ

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        try:
            verification_model = verification_to_orm(verification)

            # 既存チェック
            stmt = select(VerificationModel).where(
                VerificationModel.id == verification_model.id
            )
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # UPDATE
                existing.status = verification_model.status
                existing.result_success = verification_model.result_success
                existing.result_score = verification_model.result_score
                existing.result_confidence = verification_model.result_confidence
                existing.result_evidence = verification_model.result_evidence
                existing.completed_at = verification_model.completed_at
                existing.updated_at = datetime.now(UTC)

                # センサーデータを削除して再作成（簡易実装）
                delete_stmt = sql_delete(SensorDataModel).where(
                    SensorDataModel.verification_id == verification.id
                )
                await self._session.execute(delete_stmt)

                # 新しいセンサーデータを追加
                for sensor in verification.sensor_data:
                    sensor_model = sensor_data_to_orm(sensor, verification.id)
                    self._session.add(sensor_model)
            else:
                # INSERT
                self._session.add(verification_model)

                # センサーデータを追加
                for sensor in verification.sensor_data:
                    sensor_model = sensor_data_to_orm(sensor, verification.id)
                    self._session.add(sensor_model)

            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)

    async def find_by_id(
        self, verification_id: UUID
    ) -> Result[Verification, EntityNotFoundError]:
        """IDで検証を検索

        Args:
            verification_id: 検証ID

        Returns:
            成功: Ok(Verification)
            失敗: Err(EntityNotFoundError)
        """
        stmt = (
            select(VerificationModel)
            .where(VerificationModel.id == verification_id)
            .options(selectinload(VerificationModel.sensor_data))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Err(EntityNotFoundError("Verification", str(verification_id)))

        return Ok(orm_to_verification(model))

    async def find_by_milestone_id(
        self, milestone_id: UUID
    ) -> Result[list[Verification], Exception]:
        """マイルストーンIDで検証を検索

        Args:
            milestone_id: マイルストーンID

        Returns:
            成功: Ok(list[Verification])
            失敗: Err(Exception)
        """
        try:
            stmt = (
                select(VerificationModel)
                .where(VerificationModel.milestone_id == milestone_id)
                .options(selectinload(VerificationModel.sensor_data))
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()

            verifications = [orm_to_verification(model) for model in models]
            return Ok(verifications)
        except Exception as e:
            return Err(e)

    async def find_by_user_id(
        self, user_id: UUID
    ) -> Result[list[Verification], Exception]:
        """ユーザーIDで検証を検索

        Args:
            user_id: ユーザーID

        Returns:
            成功: Ok(list[Verification])
            失敗: Err(Exception)
        """
        try:
            stmt = (
                select(VerificationModel)
                .where(VerificationModel.user_id == user_id)
                .options(selectinload(VerificationModel.sensor_data))
            )
            result = await self._session.execute(stmt)
            models = result.scalars().all()

            verifications = [orm_to_verification(model) for model in models]
            return Ok(verifications)
        except Exception as e:
            return Err(e)

    async def delete(self, verification_id: UUID) -> Result[None, Exception]:
        """検証を削除

        Args:
            verification_id: 検証ID

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        try:
            stmt = sql_delete(VerificationModel).where(
                VerificationModel.id == verification_id
            )
            await self._session.execute(stmt)
            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)
