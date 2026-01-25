"""FastAPIの依存性注入"""

import os
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.use_cases import (
    GetCurrentUserUseCase,
    GoogleCallbackUseCase,
    GoogleLoginUseCase,
    LogoutUseCase,
)
from domain.user.models import User
from domain.user.repositories import UserRepository
from domain.milestone.repositories import MilestoneRepository
from infrastructure.auth.adapters.oauth_client import MockGoogleOAuthClient
from infrastructure.auth.adapters.token_manager import JWTTokenManager, TokenManager
from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository
from infrastructure.shared.database import get_session
from infrastructure.user.persistence.repository import PostgresUserRepository

# 外部アダプターはシングルトンで保持
_oauth_client = MockGoogleOAuthClient()
_token_manager = JWTTokenManager(
    secret_key=os.getenv(
        "JWT_SECRET_KEY", "development_secret_key_change_in_production"
    )
)


async def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """ユーザーリポジトリを取得"""
    return PostgresUserRepository(session)


async def get_milestone_repository(
    session: AsyncSession = Depends(get_session),
) -> MilestoneRepository:
    """マイルストーンリポジトリを取得"""
    return PostgresMilestoneRepository(session)


def get_oauth_client() -> MockGoogleOAuthClient:
    """OAuth2クライアントを取得"""
    return _oauth_client


def get_token_manager() -> TokenManager:
    """トークンマネージャーを取得"""
    return _token_manager


async def get_google_login_use_case(
    oauth_client: MockGoogleOAuthClient = Depends(get_oauth_client),
) -> GoogleLoginUseCase:
    """GoogleLoginUseCaseを取得"""
    return GoogleLoginUseCase(oauth_client)


async def get_google_callback_use_case(
    oauth_client: MockGoogleOAuthClient = Depends(get_oauth_client),
    user_repository: UserRepository = Depends(get_user_repository),
    token_manager: TokenManager = Depends(get_token_manager),
) -> GoogleCallbackUseCase:
    """GoogleCallbackUseCaseを取得"""
    return GoogleCallbackUseCase(oauth_client, user_repository, token_manager)


async def get_get_current_user_use_case(
    token_manager: TokenManager = Depends(get_token_manager),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetCurrentUserUseCase:
    """GetCurrentUserUseCaseを取得"""
    return GetCurrentUserUseCase(token_manager, user_repository)


def get_logout_use_case() -> LogoutUseCase:
    """LogoutUseCaseを取得"""
    return LogoutUseCase()


async def get_current_user(
    access_token: str | None = Cookie(None),
    use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
) -> User:
    """現在のユーザーを取得（認証middleware）"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await use_case.execute(access_token)
    if result.is_err():
        raise HTTPException(status_code=401, detail=result.unwrap_err())

    return result.unwrap()
