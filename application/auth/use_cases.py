"""認証ユースケース"""

from uuid import UUID
from domain.user.models import User, UserId, Email, OAuthProvider
from domain.user.repositories import UserRepository
from infrastructure.auth.adapters.oauth_client import GoogleOAuthClient
from infrastructure.auth.adapters.token_manager import TokenManager
from infrastructure.shared.result import Result, Ok, Err


class GoogleLoginUseCase:
    """Google OAuth2ログインユースケース"""

    def __init__(self, oauth_client: GoogleOAuthClient):
        """
        Args:
            oauth_client: Google OAuth2クライアント
        """
        self.oauth_client = oauth_client

    def execute(self, state: str) -> str:
        """認可URLを生成する

        Args:
            state: CSRF対策用のランダムな文字列

        Returns:
            認可URL
        """
        return self.oauth_client.get_authorization_url(state)


class GoogleCallbackUseCase:
    """Google OAuth2コールバックユースケース"""

    def __init__(
        self,
        oauth_client: GoogleOAuthClient,
        user_repository: UserRepository,
        token_manager: TokenManager,
    ):
        """
        Args:
            oauth_client: Google OAuth2クライアント
            user_repository: ユーザーリポジトリ
            token_manager: トークンマネージャー
        """
        self.oauth_client = oauth_client
        self.user_repository = user_repository
        self.token_manager = token_manager

    def execute(self, code: str) -> Result[dict[str, str], str]:
        """認可コードからユーザー情報を取得し、トークンを生成する

        Args:
            code: 認可コード

        Returns:
            成功時はOk({"access_token": str, "refresh_token": str})
            失敗時はErr(エラーメッセージ)
        """
        # 1. Googleからユーザー情報取得
        user_info_result = self.oauth_client.get_user_info(code)
        if user_info_result.is_err():
            return Err(user_info_result.unwrap_err())

        user_info = user_info_result.unwrap()

        # 2. ユーザーをDBから検索または作成
        oauth_provider = OAuthProvider(value="google")
        existing_user_result = self.user_repository.find_by_oauth(
            oauth_provider, user_info.google_user_id
        )

        if existing_user_result.is_ok():
            user = existing_user_result.unwrap()
        else:
            # 新規ユーザーを作成
            user = User.create(
                email=Email(value=user_info.email),
                oauth_provider=oauth_provider,
                oauth_user_id=user_info.google_user_id,
            )
            save_result = self.user_repository.save(user)
            if save_result.is_err():
                return Err("Failed to save user")

        # 3. トークン生成
        access_token = self.token_manager.create_access_token(
            str(user.id.value), user.email.value
        )
        refresh_token = self.token_manager.create_refresh_token(str(user.id.value))

        return Ok({"access_token": access_token, "refresh_token": refresh_token})


class GetCurrentUserUseCase:
    """現在のユーザー取得ユースケース"""

    def __init__(
        self, token_manager: TokenManager, user_repository: UserRepository
    ):
        """
        Args:
            token_manager: トークンマネージャー
            user_repository: ユーザーリポジトリ
        """
        self.token_manager = token_manager
        self.user_repository = user_repository

    def execute(self, access_token: str) -> Result[User, str]:
        """アクセストークンから現在のユーザーを取得する

        Args:
            access_token: アクセストークン

        Returns:
            成功時はOk(User)、失敗時はErr(エラーメッセージ)
        """
        # 1. トークン検証
        payload_result = self.token_manager.verify_token(access_token)
        if payload_result.is_err():
            return Err(payload_result.unwrap_err())

        payload = payload_result.unwrap()

        # 2. ユーザー取得
        user_id = UserId(value=UUID(payload.user_id))
        user_result = self.user_repository.find_by_id(user_id)
        if user_result.is_err():
            return Err("User not found")

        return Ok(user_result.unwrap())


class LogoutUseCase:
    """ログアウトユースケース"""

    def execute(self) -> Result[None, str]:
        """ログアウトする

        現時点ではトークンの無効化は実装せず、
        cookie削除のみをAPI層で行う。

        Returns:
            成功時はOk(None)
        """
        return Ok(None)
