"""認証APIルーター"""

import secrets
from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from domain.user.models import User
from application.auth.use_cases import (
    GoogleLoginUseCase,
    GoogleCallbackUseCase,
    GetCurrentUserUseCase,
    LogoutUseCase,
)
from apps.api.dependencies import (
    get_google_login_use_case,
    get_google_callback_use_case,
    get_get_current_user_use_case,
    get_logout_use_case,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class UserResponse(BaseModel):
    """ユーザーレスポンス"""

    id: str
    email: str
    status: str


@router.get("/google/login")
def google_login(
    google_login_use_case: GoogleLoginUseCase = Depends(get_google_login_use_case),
):
    """Google OAuth2ログイン

    GoogleのOAuth2認証ページにリダイレクトします。

    Returns:
        Google認証ページへのリダイレクト
    """
    state = secrets.token_urlsafe(32)
    authorization_url = google_login_use_case.execute(state)
    return RedirectResponse(url=authorization_url)


@router.get("/google/callback")
def google_callback(
    code: str,
    response: Response,
    google_callback_use_case: GoogleCallbackUseCase = Depends(
        get_google_callback_use_case
    ),
):
    """Google OAuth2コールバック

    Googleからのコールバックを処理し、JWTトークンをHTTPOnly cookieに設定します。

    Args:
        code: 認可コード
        response: Responseオブジェクト

    Returns:
        ダッシュボードへのリダイレクト

    Raises:
        HTTPException: 認証エラー
    """
    result = google_callback_use_case.execute(code)

    if result.is_err():
        raise HTTPException(status_code=400, detail=result.unwrap_err())

    tokens = result.unwrap()

    # HTTPOnly cookieにトークンを設定
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,  # 開発環境ではFalse、本番環境ではTrue
        samesite="lax",
        max_age=30 * 60,  # 30分
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,  # 開発環境ではFalse、本番環境ではTrue
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7日
    )

    return RedirectResponse(url="/dashboard")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """現在のユーザー情報を取得

    Args:
        current_user: 現在のユーザー（依存性注入）

    Returns:
        ユーザー情報
    """
    return UserResponse(
        id=str(current_user.id.value),
        email=current_user.email.value,
        status=current_user.status.status,
    )


@router.post("/logout")
def logout(
    response: Response,
    logout_use_case: LogoutUseCase = Depends(get_logout_use_case),
):
    """ログアウト

    HTTPOnly cookieからトークンを削除します。

    Args:
        response: Responseオブジェクト

    Returns:
        成功メッセージ
    """
    result = logout_use_case.execute()

    if result.is_err():
        raise HTTPException(status_code=400, detail=result.unwrap_err())

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Logged out successfully"}
