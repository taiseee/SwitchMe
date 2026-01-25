"""PostgreSQL User Repository implementation"""

from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.user.models import User, UserId, Email
from infrastructure.shared.models import UserModel
from infrastructure.user.persistence.mappers import user_to_orm, orm_to_user
from infrastructure.shared.result import Ok, Err, Result
from domain.shared.exceptions import EntityNotFoundError


class PostgresUserRepository:
    """PostgreSQL User Repository実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> Result[None, Exception]:
        """ユーザーを保存（INSERT or UPDATE）"""
        try:
            # ドメインモデル → ORMモデル変換
            user_model = user_to_orm(user)

            # 既存チェック
            stmt = select(UserModel).where(UserModel.id == user_model.id)
            result = await self._session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # UPDATE
                existing.email = user_model.email
                existing.oauth_provider = user_model.oauth_provider
                existing.oauth_user_id = user_model.oauth_user_id
                existing.status = user_model.status
                existing.last_login_at = user_model.last_login_at
                existing.updated_at = datetime.now(UTC)
            else:
                # INSERT
                self._session.add(user_model)

            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)

    async def find_by_id(self, user_id: UserId) -> Result[User, EntityNotFoundError]:
        """IDでユーザーを検索"""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Err(EntityNotFoundError("User", str(user_id.value)))

        return Ok(orm_to_user(model))

    async def find_by_email(self, email: Email) -> Result[User, EntityNotFoundError]:
        """メールアドレスでユーザーを検索"""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Err(EntityNotFoundError("User", email.value))

        return Ok(orm_to_user(model))

    async def find_by_oauth(
        self, oauth_provider: str, oauth_user_id: str
    ) -> Result[User, EntityNotFoundError]:
        """OAuthプロバイダーとユーザーIDでユーザーを検索"""
        stmt = select(UserModel).where(
            UserModel.oauth_provider == oauth_provider,
            UserModel.oauth_user_id == oauth_user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Err(EntityNotFoundError("User", f"{oauth_provider}:{oauth_user_id}"))

        return Ok(orm_to_user(model))

    async def delete(self, user_id: UserId) -> Result[None, Exception]:
        """ユーザーを削除"""
        try:
            stmt = select(UserModel).where(UserModel.id == user_id.value)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return Err(EntityNotFoundError("User", str(user_id.value)))

            await self._session.delete(model)
            await self._session.commit()
            return Ok(None)
        except Exception as e:
            await self._session.rollback()
            return Err(e)
