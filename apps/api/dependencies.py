"""FastAPIの依存性注入"""

import os
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from domain.user.models import User
from infrastructure.user.persistence.repository import PostgresUserRepository
from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository
from infrastructure.shared.database import get_session
from infrastructure.auth.adapters.oauth_client import MockGoogleOAuthClient
from infrastructure.auth.adapters.token_manager import JWTTokenManager
from application.auth.use_cases import (
    GoogleLoginUseCase,
    GoogleCallbackUseCase,
    GetCurrentUserUseCase,
    LogoutUseCase,
)

# シングルトンインスタンス（本番環境では適切なライフサイクル管理が必要）
_oauth_client = MockGoogleOAuthClient()
_token_manager = JWTTokenManager(
    secret_key=os.getenv(
        "JWT_SECRET_KEY", "development_secret_key_change_in_production"
    )
)


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresUserRepository:
    """ユーザーリポジトリを取得"""
    return PostgresUserRepository(session)


async def get_milestone_repository(
    session: AsyncSession = Depends(get_session),
) -> PostgresMilestoneRepository:
    """マイルストーンリポジトリを取得"""
    return PostgresMilestoneRepository(session)


def get_oauth_client():
    """OAuth2クライアントを取得"""
    return _oauth_client


def get_token_manager():
    """トークンマネージャーを取得"""
    return _token_manager


def get_google_login_use_case():
    """GoogleLoginUseCaseを取得"""
    return GoogleLoginUseCase(_oauth_client)


async def get_google_callback_use_case(
    user_repository: PostgresUserRepository = Depends(get_user_repository),
) -> GoogleCallbackUseCase:
    """GoogleCallbackUseCaseを取得"""
    return GoogleCallbackUseCase(_oauth_client, user_repository, _token_manager)


async def get_get_current_user_use_case(
    user_repository: PostgresUserRepository = Depends(get_user_repository),
) -> GetCurrentUserUseCase:
    """GetCurrentUserUseCaseを取得"""
    return GetCurrentUserUseCase(_token_manager, user_repository)


def get_logout_use_case():
    """LogoutUseCaseを取得"""
    return LogoutUseCase()


async def get_current_user(
    access_token: str | None = Cookie(None),
    use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
) -> User:
    """現在のユーザーを取得（認証middleware）

    Args:
        access_token: アクセストークン（cookieから取得）
        use_case: GetCurrentUserUseCaseインスタンス（依存性注入）

    Returns:
        現在のユーザー

    Raises:
        HTTPException: 認証エラー
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await use_case.execute(access_token)

    if result.is_err():
        raise HTTPException(status_code=401, detail=result.unwrap_err())

    return result.unwrap()
