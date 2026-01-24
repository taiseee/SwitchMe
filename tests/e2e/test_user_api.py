"""ユーザーAPIのE2Eテスト"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest_asyncio.fixture
async def client():
    """テスト用のHTTPクライアント"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
class TestHealthCheck:
    """ヘルスチェックAPIのテスト"""

    async def test_ヘルスチェックが正常に動作すること(self, client):
        """GET /health が正常に動作すること"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
class TestUserRegistration:
    """ユーザー登録APIのテスト"""

    async def test_ユーザー登録が成功すること(self, client):
        """POST /api/v1/users/register が正常に動作すること"""
        request_data = {
            "email": "test@example.com",
            "password": "password123",
        }
        response = await client.post("/api/v1/users/register", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data  # パスワードは返さない
        assert data["status"]["status"] == "active"

    async def test_重複メールアドレスでの登録は失敗すること(self, client):
        """同じメールアドレスでの2回目の登録は400エラーになること"""
        request_data = {
            "email": "duplicate@example.com",
            "password": "password123",
        }

        # 1回目の登録
        response1 = await client.post("/api/v1/users/register", json=request_data)
        assert response1.status_code == 201

        # 2回目の登録（重複）
        response2 = await client.post("/api/v1/users/register", json=request_data)
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data

    async def test_無効なメールアドレスは拒否されること(self, client):
        """無効なメールアドレス形式は422エラーになること"""
        request_data = {
            "email": "invalid-email",
            "password": "password123",
        }
        response = await client.post("/api/v1/users/register", json=request_data)
        assert response.status_code == 422  # Validation Error

    async def test_短いパスワードは拒否されること(self, client):
        """8文字未満のパスワードは422エラーになること"""
        request_data = {
            "email": "test@example.com",
            "password": "short",
        }
        response = await client.post("/api/v1/users/register", json=request_data)
        assert response.status_code == 422  # Validation Error
