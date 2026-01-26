"""認証ユースケースのテスト"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from application.auth.use_cases import (
    GoogleLoginUseCase,
    GoogleCallbackUseCase,
    GetCurrentUserUseCase,
    LogoutUseCase,
)
from domain.shared.exceptions import EntityNotFoundError
from domain.user.models import Email, OAuthProvider, User
from domain.user.repositories import UserRepository
from infrastructure.auth.adapters.oauth_client import GoogleOAuthClient, GoogleUserInfo
from infrastructure.auth.adapters.token_manager import TokenManager, TokenPayload
from infrastructure.shared.result import Ok, Err


@pytest.fixture
def oauth_client():
    """テスト用のOAuth2クライアント"""
    return Mock(spec=GoogleOAuthClient)


@pytest.fixture
def user_repository():
    """テスト用のユーザーリポジトリ"""
    repository = Mock(spec=UserRepository)
    repository.save = AsyncMock()
    repository.find_by_id = AsyncMock()
    repository.find_by_email = AsyncMock()
    repository.find_by_oauth = AsyncMock()
    repository.delete = AsyncMock()
    return repository


@pytest.fixture
def token_manager():
    """テスト用のトークンマネージャー"""
    return Mock(spec=TokenManager)


class TestGoogleLoginUseCase:
    """GoogleLoginUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_認可URLを生成できること(self, oauth_client):
        """認可URLを生成できること"""
        expected_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?state=test_state_123"
        )
        oauth_client.get_authorization_url.return_value = expected_url
        use_case = GoogleLoginUseCase(oauth_client)

        state = "test_state_123"
        url = await use_case.execute(state)

        assert url == expected_url
        oauth_client.get_authorization_url.assert_called_once_with(state)


class TestGoogleCallbackUseCase:
    """GoogleCallbackUseCaseのテスト"""

    @pytest.fixture
    def use_case(self, oauth_client, user_repository, token_manager):
        """テスト用のGoogleCallbackUseCase"""
        return GoogleCallbackUseCase(oauth_client, user_repository, token_manager)

    @pytest.mark.anyio
    async def test_新規ユーザーの場合はユーザーを作成してトークンを返すこと(
        self, use_case, oauth_client, user_repository, token_manager
    ):
        """新規ユーザーの場合はユーザーを作成してトークンを返すこと"""
        oauth_client.get_user_info.return_value = Ok(
            GoogleUserInfo(
                email="mock@example.com",
                google_user_id="mock_google_user_123",
                name="Mock User",
            )
        )
        user_repository.find_by_oauth.return_value = Err(
            EntityNotFoundError("User", "google:mock_google_user_123")
        )
        user_repository.save.return_value = Ok(None)
        token_manager.create_access_token.return_value = "access_token"
        token_manager.create_refresh_token.return_value = "refresh_token"

        code = "valid_code"
        result = await use_case.execute(code)

        assert result.is_ok()
        tokens = result.unwrap()
        assert tokens == {"access_token": "access_token", "refresh_token": "refresh_token"}

        oauth_client.get_user_info.assert_called_once_with(code)
        user_repository.find_by_oauth.assert_awaited_once_with(
            OAuthProvider(value="google"), "mock_google_user_123"
        )
        user_repository.save.assert_awaited_once()
        saved_user = user_repository.save.await_args.args[0]
        assert saved_user.email.value == "mock@example.com"
        assert saved_user.oauth_user_id == "mock_google_user_123"
        token_manager.create_access_token.assert_called_once_with(
            str(saved_user.id.value), saved_user.email.value
        )
        token_manager.create_refresh_token.assert_called_once_with(
            str(saved_user.id.value)
        )

    @pytest.mark.anyio
    async def test_既存ユーザーの場合はトークンを返すこと(
        self, use_case, oauth_client, user_repository, token_manager
    ):
        """既存ユーザーの場合はトークンを返すこと"""
        existing_user = User.create(
            email=Email(value="mock@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="mock_google_user_123",
        )
        oauth_client.get_user_info.return_value = Ok(
            GoogleUserInfo(
                email="mock@example.com",
                google_user_id="mock_google_user_123",
                name="Mock User",
            )
        )
        user_repository.find_by_oauth.return_value = Ok(existing_user)
        token_manager.create_access_token.return_value = "access_token"
        token_manager.create_refresh_token.return_value = "refresh_token"

        code = "valid_code"
        result = await use_case.execute(code)

        assert result.is_ok()
        tokens = result.unwrap()
        assert tokens == {"access_token": "access_token", "refresh_token": "refresh_token"}

        oauth_client.get_user_info.assert_called_once_with(code)
        user_repository.find_by_oauth.assert_awaited_once_with(
            OAuthProvider(value="google"), "mock_google_user_123"
        )
        user_repository.save.assert_not_awaited()
        token_manager.create_access_token.assert_called_once_with(
            str(existing_user.id.value), existing_user.email.value
        )
        token_manager.create_refresh_token.assert_called_once_with(
            str(existing_user.id.value)
        )

    @pytest.mark.anyio
    async def test_不正なコードの場合はエラーを返すこと(
        self, use_case, oauth_client, user_repository, token_manager
    ):
        """不正なコードの場合はエラーを返すこと"""
        oauth_client.get_user_info.return_value = Err("Invalid authorization code")

        result = await use_case.execute("invalid_code")

        assert result.is_err()
        assert "Invalid authorization code" in result.unwrap_err()
        user_repository.find_by_oauth.assert_not_awaited()
        user_repository.save.assert_not_awaited()
        token_manager.create_access_token.assert_not_called()
        token_manager.create_refresh_token.assert_not_called()


class TestGetCurrentUserUseCase:
    """GetCurrentUserUseCaseのテスト"""

    @pytest.fixture
    def use_case(self, token_manager, user_repository):
        """テスト用のGetCurrentUserUseCase"""
        return GetCurrentUserUseCase(token_manager, user_repository)

    @pytest.mark.anyio
    async def test_有効なトークンでユーザーを取得できること(
        self, use_case, token_manager, user_repository
    ):
        """有効なトークンでユーザーを取得できること"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        token_manager.verify_token.return_value = Ok(
            TokenPayload(
                user_id=str(user.id.value),
                email=user.email.value,
                exp=123,
            )
        )
        user_repository.find_by_id.return_value = Ok(user)

        access_token = "valid.token.value"
        result = await use_case.execute(access_token)

        assert result.is_ok()
        retrieved_user = result.unwrap()
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
        token_manager.verify_token.assert_called_once_with(access_token)
        user_repository.find_by_id.assert_awaited_once_with(user.id)

    @pytest.mark.anyio
    async def test_不正なトークンの場合はエラーを返すこと(
        self, use_case, token_manager, user_repository
    ):
        """不正なトークンの場合はエラーを返すこと"""
        token_manager.verify_token.return_value = Err("Invalid token")

        result = await use_case.execute("invalid.token.value")

        assert result.is_err()
        assert "Invalid token" in result.unwrap_err()
        user_repository.find_by_id.assert_not_awaited()

    @pytest.mark.anyio
    async def test_存在しないユーザーのトークンの場合はエラーを返すこと(
        self, use_case, token_manager, user_repository
    ):
        """存在しないユーザーのトークンの場合はエラーを返すこと"""
        non_existent_user_id = str(uuid4())
        token_manager.verify_token.return_value = Ok(
            TokenPayload(
                user_id=non_existent_user_id,
                email="nonexistent@example.com",
                exp=123,
            )
        )
        user_repository.find_by_id.return_value = Err(
            EntityNotFoundError("User", non_existent_user_id)
        )

        result = await use_case.execute("valid.token.value")

        assert result.is_err()
        assert "User not found" in result.unwrap_err()
        user_repository.find_by_id.assert_awaited_once()


class TestLogoutUseCase:
    """LogoutUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_ログアウトできること(self):
        """ログアウトできること（現時点ではcookie削除のみ）"""
        use_case = LogoutUseCase()

        result = await use_case.execute()

        assert result.is_ok()
        assert result.unwrap() is None
