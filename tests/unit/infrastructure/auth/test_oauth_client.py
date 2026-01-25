"""GoogleOAuthClientのテスト"""

from infrastructure.auth.adapters.oauth_client import (
    GoogleUserInfo,
    MockGoogleOAuthClient,
)


class TestMockGoogleOAuthClient:
    """MockGoogleOAuthClientのテスト"""

    def test_認可URLを生成できること(self):
        """認可URLを生成できること"""
        client = MockGoogleOAuthClient()
        state = "test_state_123"
        url = client.get_authorization_url(state)

        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert state in url

    def test_正しいコードでユーザー情報を取得できること(self):
        """正しいコードでユーザー情報を取得できること"""
        client = MockGoogleOAuthClient()
        code = "valid_code"

        result = client.get_user_info(code)

        assert result.is_ok()
        user_info = result.unwrap()
        assert isinstance(user_info, GoogleUserInfo)
        assert user_info.email == "mock@example.com"
        assert user_info.google_user_id == "mock_google_user_123"
        assert user_info.name == "Mock User"

    def test_不正なコードではエラーを返すこと(self):
        """不正なコードではエラーを返すこと"""
        client = MockGoogleOAuthClient()
        code = "invalid_code"

        result = client.get_user_info(code)

        assert result.is_err()
        assert "Invalid authorization code" in result.unwrap_err()


class TestGoogleUserInfo:
    """GoogleUserInfoのテスト"""

    def test_ユーザー情報を作成できること(self):
        """ユーザー情報を作成できること"""
        user_info = GoogleUserInfo(
            email="test@example.com",
            google_user_id="google_123",
            name="Test User",
        )

        assert user_info.email == "test@example.com"
        assert user_info.google_user_id == "google_123"
        assert user_info.name == "Test User"
