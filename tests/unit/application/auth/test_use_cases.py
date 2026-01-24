"""認証ユースケースのテスト"""

import pytest
from uuid import uuid4
from domain.user.models import User, UserId, Email, OAuthProvider
from domain.user.repositories import InMemoryUserRepository
from infrastructure.auth.adapters.oauth_client import MockGoogleOAuthClient
from infrastructure.auth.adapters.token_manager import JWTTokenManager
from application.auth.use_cases import (
    GoogleLoginUseCase,
    GoogleCallbackUseCase,
    GetCurrentUserUseCase,
    LogoutUseCase,
)


class TestGoogleLoginUseCase:
    """GoogleLoginUseCaseのテスト"""

    def test_認可URLを生成できること(self):
        """認可URLを生成できること"""
        oauth_client = MockGoogleOAuthClient()
        use_case = GoogleLoginUseCase(oauth_client)

        state = "test_state_123"
        url = use_case.execute(state)

        assert isinstance(url, str)
        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert state in url


class TestGoogleCallbackUseCase:
    """GoogleCallbackUseCaseのテスト"""

    @pytest.fixture
    def oauth_client(self):
        """テスト用のOAuth2クライアント"""
        return MockGoogleOAuthClient()

    @pytest.fixture
    def user_repository(self):
        """テスト用のユーザーリポジトリ"""
        return InMemoryUserRepository()

    @pytest.fixture
    def token_manager(self):
        """テスト用のトークンマネージャー"""
        return JWTTokenManager(secret_key="test_secret")

    @pytest.fixture
    def use_case(self, oauth_client, user_repository, token_manager):
        """テスト用のGoogleCallbackUseCase"""
        return GoogleCallbackUseCase(oauth_client, user_repository, token_manager)

    def test_新規ユーザーの場合はユーザーを作成してトークンを返すこと(
        self, use_case, user_repository
    ):
        """新規ユーザーの場合はユーザーを作成してトークンを返すこと"""
        code = "valid_code"

        result = use_case.execute(code)

        assert result.is_ok()
        tokens = result.unwrap()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)

        # ユーザーが作成されていることを確認
        user_result = user_repository.find_by_oauth(
            OAuthProvider(value="google"), "mock_google_user_123"
        )
        assert user_result.is_ok()

    def test_既存ユーザーの場合はトークンを返すこと(
        self, use_case, user_repository
    ):
        """既存ユーザーの場合はトークンを返すこと"""
        # 事前にユーザーを作成
        existing_user = User.create(
            email=Email(value="mock@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="mock_google_user_123",
        )
        user_repository.save(existing_user)

        code = "valid_code"
        result = use_case.execute(code)

        assert result.is_ok()
        tokens = result.unwrap()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    def test_不正なコードの場合はエラーを返すこと(self, use_case):
        """不正なコードの場合はエラーを返すこと"""
        code = "invalid_code"

        result = use_case.execute(code)

        assert result.is_err()
        assert "Invalid authorization code" in result.unwrap_err()


class TestGetCurrentUserUseCase:
    """GetCurrentUserUseCaseのテスト"""

    @pytest.fixture
    def token_manager(self):
        """テスト用のトークンマネージャー"""
        return JWTTokenManager(secret_key="test_secret")

    @pytest.fixture
    def user_repository(self):
        """テスト用のユーザーリポジトリ"""
        return InMemoryUserRepository()

    @pytest.fixture
    def use_case(self, token_manager, user_repository):
        """テスト用のGetCurrentUserUseCase"""
        return GetCurrentUserUseCase(token_manager, user_repository)

    def test_有効なトークンでユーザーを取得できること(
        self, use_case, token_manager, user_repository
    ):
        """有効なトークンでユーザーを取得できること"""
        # ユーザーを作成して保存
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        user_repository.save(user)

        # トークンを生成
        access_token = token_manager.create_access_token(
            str(user.id.value), user.email.value
        )

        # ユーザーを取得
        result = use_case.execute(access_token)

        assert result.is_ok()
        retrieved_user = result.unwrap()
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email

    def test_不正なトークンの場合はエラーを返すこと(self, use_case):
        """不正なトークンの場合はエラーを返すこと"""
        invalid_token = "invalid.token.value"

        result = use_case.execute(invalid_token)

        assert result.is_err()
        assert "Invalid token" in result.unwrap_err()

    def test_存在しないユーザーのトークンの場合はエラーを返すこと(
        self, use_case, token_manager
    ):
        """存在しないユーザーのトークンの場合はエラーを返すこと"""
        # 存在しないユーザーのトークンを生成
        non_existent_user_id = str(uuid4())
        access_token = token_manager.create_access_token(
            non_existent_user_id, "nonexistent@example.com"
        )

        result = use_case.execute(access_token)

        assert result.is_err()
        assert "User not found" in result.unwrap_err()


class TestLogoutUseCase:
    """LogoutUseCaseのテスト"""

    def test_ログアウトできること(self):
        """ログアウトできること（現時点ではcookie削除のみ）"""
        use_case = LogoutUseCase()

        result = use_case.execute()

        assert result.is_ok()
        assert result.unwrap() is None
