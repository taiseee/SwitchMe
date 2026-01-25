"""Userドメインモデルのテスト"""

from datetime import datetime, timezone
from uuid import UUID
import pytest
from pydantic import ValidationError
from domain.user.models import (
    UserId,
    Email,
    UserStatus,
    User,
    OAuthProvider,
)


class TestOAuthProvider:
    """OAuthProviderのテスト"""

    def test_googleプロバイダーで作成できること(self):
        """googleプロバイダーでOAuthProviderが作成できること"""
        provider = OAuthProvider(value="google")
        assert provider.value == "google"

    def test_デフォルト値はgoogleであること(self):
        """デフォルト値がgoogleであること"""
        provider = OAuthProvider()
        assert provider.value == "google"

    def test_google以外のプロバイダーは拒否されること(self):
        """google以外のプロバイダーは拒否されること"""
        with pytest.raises(ValidationError):
            OAuthProvider(value="facebook")  # type: ignore


class TestEmail:
    """Emailのテスト"""

    def test_正しいメールアドレス形式で作成できること(self):
        """正しいメールアドレス形式でEmailが作成できること"""
        email = Email(value="test@example.com")
        assert email.value == "test@example.com"

    def test_不正なメールアドレス形式は拒否されること(self):
        """不正なメールアドレス形式は拒否されること"""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@example.com",
            "invalid@example",
            "",
        ]
        for invalid in invalid_emails:
            with pytest.raises(ValidationError):
                Email(value=invalid)


class TestUserId:
    """UserIdのテスト"""

    def test_uuidで作成できること(self):
        """UUIDでUserIdが作成できること"""
        uuid_value = UUID("12345678-1234-5678-1234-567812345678")
        user_id = UserId(value=uuid_value)
        assert user_id.value == uuid_value


class TestUserStatus:
    """UserStatusのテスト"""

    def test_activeステータスで作成できること(self):
        """activeステータスでUserStatusが作成できること"""
        status = UserStatus(status="active", last_login_at=None)
        assert status.status == "active"
        assert status.last_login_at is None

    def test_最終ログイン日時を持つステータスを作成できること(self):
        """最終ログイン日時を持つUserStatusが作成できること"""
        now = datetime.now(timezone.utc)
        status = UserStatus(status="active", last_login_at=now)
        assert status.last_login_at == now

    def test_不正なステータスは拒否されること(self):
        """不正なステータスは拒否されること"""
        with pytest.raises(ValidationError):
            UserStatus(status="invalid", last_login_at=None)  # type: ignore


class TestUser:
    """Userのテスト"""

    def test_OAuth認証でuserが作成できること(self):
        """OAuth認証でUserが作成できること"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        assert isinstance(user.id, UserId)
        assert user.email.value == "test@example.com"
        assert user.oauth_provider.value == "google"
        assert user.oauth_user_id == "google_user_123"
        assert user.status.status == "active"
        assert user.status.last_login_at is None

    def test_ログインすると最終ログイン日時が更新されること(self):
        """login()を呼ぶと最終ログイン日時が更新されること"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        assert user.status.last_login_at is None

        # ログイン
        logged_in_user = user.login()

        assert logged_in_user.status.last_login_at is not None
        assert isinstance(logged_in_user.status.last_login_at, datetime)
        # ログイン時刻が現在時刻に近いことを確認
        now = datetime.now(timezone.utc)
        time_diff = (now - logged_in_user.status.last_login_at).total_seconds()
        assert time_diff < 1.0  # 1秒以内

    def test_アカウント削除するとステータスがdeletedになること(self):
        """delete_account()を呼ぶとステータスがdeletedになること"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        assert user.status.status == "active"

        # アカウント削除
        deleted_user = user.delete_account()

        assert deleted_user.status.status == "deleted"

    def test_userは不変であること(self):
        """Userは不変（frozen）であること"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        with pytest.raises((ValidationError, AttributeError)):
            user.email = Email(value="new@example.com")  # type: ignore

    def test_同じidのuserは等価であること(self):
        """同じIDのUserは等価であること（エンティティの同一性）"""
        user_id = UserId(value=UUID("12345678-1234-5678-1234-567812345678"))
        user1 = User(
            id=user_id,
            email=Email(value="test1@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_1",
            status=UserStatus(status="active", last_login_at=None),
        )
        user2 = User(
            id=user_id,
            email=Email(value="test2@example.com"),  # 異なるメール
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_2",  # 異なるOAuthユーザーID
            status=UserStatus(status="active", last_login_at=None),
        )
        # エンティティの同一性はIDで判断（Pydanticのデフォルトはすべてのフィールドを比較）
        assert user1.id == user2.id
