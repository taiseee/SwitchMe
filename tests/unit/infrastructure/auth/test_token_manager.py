"""JWTTokenManagerのテスト"""

import pytest
from datetime import datetime, timedelta, timezone
from infrastructure.auth.adapters.token_manager import (
    JWTTokenManager,
    TokenPayload,
)


class TestJWTTokenManager:
    """JWTTokenManagerのテスト"""

    @pytest.fixture
    def token_manager(self):
        """テスト用のトークンマネージャー"""
        return JWTTokenManager(secret_key="test_secret_key")

    def test_アクセストークンを生成できること(self, token_manager):
        """アクセストークンを生成できること"""
        user_id = "12345678-1234-5678-1234-567812345678"
        email = "test@example.com"

        token = token_manager.create_access_token(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_リフレッシュトークンを生成できること(self, token_manager):
        """リフレッシュトークンを生成できること"""
        user_id = "12345678-1234-5678-1234-567812345678"

        token = token_manager.create_refresh_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_有効なトークンを検証できること(self, token_manager):
        """有効なトークンを検証できること"""
        user_id = "12345678-1234-5678-1234-567812345678"
        email = "test@example.com"

        token = token_manager.create_access_token(user_id, email)
        result = token_manager.verify_token(token)

        assert result.is_ok()
        payload = result.unwrap()
        assert isinstance(payload, TokenPayload)
        assert payload.user_id == user_id
        assert payload.email == email
        assert isinstance(payload.exp, int)

    def test_不正なトークンは検証に失敗すること(self, token_manager):
        """不正なトークンは検証に失敗すること"""
        invalid_token = "invalid.token.value"

        result = token_manager.verify_token(invalid_token)

        assert result.is_err()
        assert "Invalid token" in result.unwrap_err()

    def test_異なる秘密鍵で生成されたトークンは検証に失敗すること(self):
        """異なる秘密鍵で生成されたトークンは検証に失敗すること"""
        manager1 = JWTTokenManager(secret_key="secret1")
        manager2 = JWTTokenManager(secret_key="secret2")

        user_id = "12345678-1234-5678-1234-567812345678"
        email = "test@example.com"

        token = manager1.create_access_token(user_id, email)
        result = manager2.verify_token(token)

        assert result.is_err()
        assert "Invalid token" in result.unwrap_err()


class TestTokenPayload:
    """TokenPayloadのテスト"""

    def test_トークンペイロードを作成できること(self):
        """トークンペイロードを作成できること"""
        payload = TokenPayload(
            user_id="12345678-1234-5678-1234-567812345678",
            email="test@example.com",
            exp=int(
                (datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()
            ),
        )

        assert payload.user_id == "12345678-1234-5678-1234-567812345678"
        assert payload.email == "test@example.com"
        assert isinstance(payload.exp, int)
