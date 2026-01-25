"""認証API統合テスト"""

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.dependencies import get_token_manager
from domain.user.models import Email, OAuthProvider, User
from infrastructure.user.persistence.repository import PostgresUserRepository


class TestAuthAPI:
    """認証APIの統合テスト"""

    async def _create_authenticated_user(self, db_session):
        """認証済みユーザーを作成してトークンを返す"""
        repository = PostgresUserRepository(db_session)
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        await repository.save(user)

        token_manager = get_token_manager()
        access_token = token_manager.create_access_token(
            str(user.id.value), user.email.value
        )
        return user, access_token

    @pytest.mark.anyio
    async def test_Google認可URLにリダイレクトできること(self, app_with_db):
        """GET /api/v1/auth/google/loginでGoogle認可URLにリダイレクトできること"""
        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/auth/google/login", follow_redirects=False
            )

        assert response.status_code == 307
        assert "location" in response.headers
        assert (
            "https://accounts.google.com/o/oauth2/v2/auth"
            in response.headers["location"]
        )

    @pytest.mark.anyio
    async def test_正しいコードでコールバックが成功すること(self, app_with_db):
        """GET /api/v1/auth/google/callbackで正しいコードで認証が成功すること"""
        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/auth/google/callback?code=valid_code",
                follow_redirects=False,
            )

        assert response.status_code == 307
        assert response.headers["location"] == "/dashboard"

    @pytest.mark.anyio
    async def test_不正なコードでコールバックが失敗すること(self, app_with_db):
        """GET /api/v1/auth/google/callbackで不正なコードで認証が失敗すること"""
        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/auth/google/callback?code=invalid_code"
            )

        assert response.status_code == 400
        assert "Invalid authorization code" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_認証済みユーザーの情報を取得できること(self, app_with_db, db_session):
        """GET /api/v1/auth/meで認証済みユーザーの情報を取得できること"""
        user, access_token = await self._create_authenticated_user(db_session)

        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/auth/me", cookies={"access_token": access_token}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user.id.value)
        assert data["email"] == user.email.value
        assert data["status"] == user.status.status

    @pytest.mark.anyio
    async def test_未認証ユーザーは401エラーになること(self, app_with_db):
        """GET /api/v1/auth/meで未認証ユーザーは401エラーになること"""
        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_不正なトークンは401エラーになること(self, app_with_db):
        """GET /api/v1/auth/meで不正なトークンは401エラーになること"""
        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/v1/auth/me", cookies={"access_token": "invalid.token.value"}
            )

        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_ログアウトできること(self, app_with_db, db_session):
        """POST /api/v1/auth/logoutでログアウトできること"""
        _, access_token = await self._create_authenticated_user(db_session)

        async with AsyncClient(
            transport=ASGITransport(app=app_with_db), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/logout", cookies={"access_token": access_token}
            )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
