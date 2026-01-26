"""Milestone API統合テスト"""

import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from domain.user.models import User, Email, OAuthProvider
from apps.api.dependencies import _token_manager
from infrastructure.shared.database import get_session_maker
from infrastructure.user.persistence.repository import PostgresUserRepository


class TestMilestoneAPI:
    """Milestone APIの統合テスト"""

    async def _create_authenticated_user(self):
        """認証済みユーザーを作成してトークンを返す"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )

        # セッションとリポジトリを取得してユーザーを保存
        session_maker = get_session_maker()
        async with session_maker() as session:
            repository = PostgresUserRepository(session)
            await repository.save(user)

        access_token = _token_manager.create_access_token(
            str(user.id.value), user.email.value
        )
        return user, access_token

    @pytest.mark.anyio
    async def test_未認証ユーザーはマイルストーン作成できないこと(self):
        """POST /api/v1/milestonesで未認証ユーザーは401エラーになること"""
        milestone_data = {
            "title": "朝のランニング",
            "deadline_date": "2026-01-26",
            "deadline_time": "07:00:00",
            "timezone": "Asia/Tokyo",
            "verification_type": "location",
            "verification_conditions": {"lat": 35.6812, "lon": 139.7671},
            "verification_threshold": 100.0,
            "penalty_amount": 1000,
            "penalty_currency": "JPY",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/milestones", json=milestone_data)

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_認証済みユーザーはマイルストーン作成できること(self):
        """POST /api/v1/milestonesで認証済みユーザーはマイルストーンを作成できること"""
        user, access_token = await self._create_authenticated_user()

        milestone_data = {
            "title": "朝のランニング",
            "deadline_date": "2026-01-26",
            "deadline_time": "07:00:00",
            "timezone": "Asia/Tokyo",
            "verification_type": "location",
            "verification_conditions": {"lat": 35.6812, "lon": 139.7671},
            "verification_threshold": 100.0,
            "penalty_amount": 1000,
            "penalty_currency": "JPY",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/milestones",
                json=milestone_data,
                cookies={"access_token": access_token},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "朝のランニング"
        assert data["user_id"] == str(user.id.value)

    @pytest.mark.anyio
    async def test_認証済みユーザーはマイルストーン一覧を取得できること(self):
        """GET /api/v1/milestonesで認証済みユーザーはマイルストーン一覧を取得できること"""
        _, access_token = await self._create_authenticated_user()

        # マイルストーンを作成
        milestone_data = {
            "title": "朝のランニング",
            "deadline_date": "2026-01-26",
            "deadline_time": "07:00:00",
            "timezone": "Asia/Tokyo",
            "verification_type": "location",
            "verification_conditions": {"lat": 35.6812, "lon": 139.7671},
            "verification_threshold": 100.0,
            "penalty_amount": 1000,
            "penalty_currency": "JPY",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.post(
                "/api/v1/milestones",
                json=milestone_data,
                cookies={"access_token": access_token},
            )

            # マイルストーン一覧を取得
            response = await client.get(
                "/api/v1/milestones", cookies={"access_token": access_token}
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "朝のランニング"

    @pytest.mark.anyio
    async def test_未認証ユーザーはマイルストーン一覧を取得できないこと(self):
        """GET /api/v1/milestonesで未認証ユーザーは401エラーになること"""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/milestones")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_認証済みユーザーはマイルストーンを更新できること(self):
        """PUT /api/v1/milestones/{milestone_id}で認証済みユーザーはマイルストーンを更新できること"""
        _, access_token = await self._create_authenticated_user()

        # マイルストーンを作成
        milestone_data = {
            "title": "朝のランニング",
            "deadline_date": "2026-01-26",
            "deadline_time": "07:00:00",
            "timezone": "Asia/Tokyo",
            "verification_type": "location",
            "verification_conditions": {"lat": 35.6812, "lon": 139.7671},
            "verification_threshold": 100.0,
            "penalty_amount": 1000,
            "penalty_currency": "JPY",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_response = await client.post(
                "/api/v1/milestones",
                json=milestone_data,
                cookies={"access_token": access_token},
            )
            milestone_id = create_response.json()["id"]

            # マイルストーンを更新
            update_data = {"title": "朝のジョギング"}

            response = await client.put(
                f"/api/v1/milestones/{milestone_id}",
                json=update_data,
                cookies={"access_token": access_token},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "朝のジョギング"

    @pytest.mark.anyio
    async def test_認証済みユーザーはマイルストーンを削除できること(self):
        """DELETE /api/v1/milestones/{milestone_id}で認証済みユーザーはマイルストーンを削除できること"""
        _, access_token = await self._create_authenticated_user()

        # マイルストーンを作成
        milestone_data = {
            "title": "朝のランニング",
            "deadline_date": "2026-01-26",
            "deadline_time": "07:00:00",
            "timezone": "Asia/Tokyo",
            "verification_type": "location",
            "verification_conditions": {"lat": 35.6812, "lon": 139.7671},
            "verification_threshold": 100.0,
            "penalty_amount": 1000,
            "penalty_currency": "JPY",
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_response = await client.post(
                "/api/v1/milestones",
                json=milestone_data,
                cookies={"access_token": access_token},
            )
            milestone_id = create_response.json()["id"]

            # マイルストーンを削除
            response = await client.delete(
                f"/api/v1/milestones/{milestone_id}",
                cookies={"access_token": access_token},
            )

            assert response.status_code == 200

            # 一覧取得で確認
            list_response = await client.get(
                "/api/v1/milestones", cookies={"access_token": access_token}
            )
            assert len(list_response.json()) == 0
