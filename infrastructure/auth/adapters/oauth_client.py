"""Google OAuth2クライアントアダプター"""

from typing import Protocol
from pydantic import BaseModel
from infrastructure.shared.result import Result, Ok, Err


class GoogleUserInfo(BaseModel):
    """Googleユーザー情報"""

    email: str
    google_user_id: str
    name: str


class GoogleOAuthClient(Protocol):
    """Google OAuth2クライアントのインターフェース"""

    def get_authorization_url(self, state: str) -> str:
        """認可URLを生成する

        Args:
            state: CSRF対策用のランダムな文字列

        Returns:
            認可URL
        """
        ...

    def get_user_info(self, code: str) -> Result[GoogleUserInfo, str]:
        """認可コードからユーザー情報を取得する

        Args:
            code: 認可コード

        Returns:
            成功時はOk(GoogleUserInfo)、失敗時はErr(エラーメッセージ)
        """
        ...


class MockGoogleOAuthClient:
    """テスト用のモックGoogle OAuth2クライアント"""

    def get_authorization_url(self, state: str) -> str:
        """認可URLを生成する（モック）"""
        return f"https://accounts.google.com/o/oauth2/v2/auth?state={state}&client_id=mock_client_id"

    def get_user_info(self, code: str) -> Result[GoogleUserInfo, str]:
        """認可コードからユーザー情報を取得する（モック）"""
        if code == "invalid_code":
            return Err("Invalid authorization code")

        return Ok(
            GoogleUserInfo(
                email="mock@example.com",
                google_user_id="mock_google_user_123",
                name="Mock User",
            )
        )


class AuthlibGoogleOAuthClient:
    """AuthlibベースのGoogle OAuth2クライアント実装"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Args:
            client_id: Google Cloud ConsoleのクライアントID
            client_secret: Google Cloud Consoleのクライアントシークレット
            redirect_uri: リダイレクトURI
        """
        from authlib.integrations.httpx_client import OAuth2Client

        self.client = OAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="openid email profile",
            token_endpoint="https://oauth2.googleapis.com/token",
            authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
        )

    def get_authorization_url(self, state: str) -> str:
        """認可URLを生成する"""
        url, _ = self.client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth", state=state
        )
        return url

    def get_user_info(self, code: str) -> Result[GoogleUserInfo, str]:
        """認可コードからユーザー情報を取得する"""
        try:
            # トークンを取得
            token = self.client.fetch_token(
                "https://oauth2.googleapis.com/token", code=code
            )

            # ユーザー情報を取得
            resp = self.client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                token=token,
            )
            resp.raise_for_status()
            user_data = resp.json()

            return Ok(
                GoogleUserInfo(
                    email=user_data["email"],
                    google_user_id=user_data["id"],
                    name=user_data.get("name", ""),
                )
            )
        except Exception as e:
            return Err(str(e))
