"""FastAPIの依存性注入"""

import os
from fastapi import Cookie, HTTPException
from domain.user.models import User
from domain.user.repositories import InMemoryUserRepository
from domain.milestone.repositories import InMemoryMilestoneRepository
from infrastructure.auth.adapters.oauth_client import MockGoogleOAuthClient
from infrastructure.auth.adapters.token_manager import JWTTokenManager
from application.auth.use_cases import (
    GoogleLoginUseCase,
    GoogleCallbackUseCase,
    GetCurrentUserUseCase,
    LogoutUseCase,
)

# シングルトンインスタンス（本番環境では適切なライフサイクル管理が必要）
_user_repository = InMemoryUserRepository()
_milestone_repository = InMemoryMilestoneRepository()
_oauth_client = MockGoogleOAuthClient()
_token_manager = JWTTokenManager(
    secret_key=os.getenv(
        "JWT_SECRET_KEY", "development_secret_key_change_in_production"
    )
)


def get_user_repository():
    """ユーザーリポジトリを取得"""
    return _user_repository


def get_milestone_repository():
    """マイルストーンリポジトリを取得"""
    return _milestone_repository


def get_oauth_client():
    """OAuth2クライアントを取得"""
    return _oauth_client


def get_token_manager():
    """トークンマネージャーを取得"""
    return _token_manager


def get_google_login_use_case():
    """GoogleLoginUseCaseを取得"""
    return GoogleLoginUseCase(_oauth_client)


def get_google_callback_use_case():
    """GoogleCallbackUseCaseを取得"""
    return GoogleCallbackUseCase(_oauth_client, _user_repository, _token_manager)


def get_get_current_user_use_case():
    """GetCurrentUserUseCaseを取得"""
    return GetCurrentUserUseCase(_token_manager, _user_repository)


def get_logout_use_case():
    """LogoutUseCaseを取得"""
    return LogoutUseCase()


def get_current_user(
    access_token: str | None = Cookie(None),
) -> User:
    """現在のユーザーを取得（認証middleware）

    Args:
        access_token: アクセストークン（cookieから取得）

    Returns:
        現在のユーザー

    Raises:
        HTTPException: 認証エラー
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    use_case = get_get_current_user_use_case()
    result = use_case.execute(access_token)

    if result.is_err():
        raise HTTPException(status_code=401, detail=result.unwrap_err())

    return result.unwrap()
