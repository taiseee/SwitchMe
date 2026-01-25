"""Milestone API統合テスト"""

from fastapi.testclient import TestClient
from apps.api.main import app
from domain.user.models import User, Email, OAuthProvider
from apps.api.dependencies import (
    _user_repository,
    _milestone_repository,
    _token_manager,
)

client = TestClient(app)


class TestMilestoneAPI:
    """Milestone APIの統合テスト"""

    def setup_method(self):
        """各テストメソッドの前に実行"""
        # リポジトリをクリア
        _user_repository._users.clear()
        _milestone_repository._milestones.clear()

    def _create_authenticated_user(self):
        """認証済みユーザーを作成してトークンを返す"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        _user_repository.save(user)

        access_token = _token_manager.create_access_token(
            str(user.id.value), user.email.value
        )
        return user, access_token

    def test_未認証ユーザーはマイルストーン作成できないこと(self):
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

        response = client.post("/api/v1/milestones", json=milestone_data)

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_認証済みユーザーはマイルストーン作成できること(self):
        """POST /api/v1/milestonesで認証済みユーザーはマイルストーンを作成できること"""
        user, access_token = self._create_authenticated_user()

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

        response = client.post(
            "/api/v1/milestones",
            json=milestone_data,
            cookies={"access_token": access_token},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "朝のランニング"
        assert data["user_id"] == str(user.id.value)

    def test_認証済みユーザーはマイルストーン一覧を取得できること(self):
        """GET /api/v1/milestonesで認証済みユーザーはマイルストーン一覧を取得できること"""
        user, access_token = self._create_authenticated_user()

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

        client.post(
            "/api/v1/milestones",
            json=milestone_data,
            cookies={"access_token": access_token},
        )

        # マイルストーン一覧を取得
        response = client.get(
            "/api/v1/milestones", cookies={"access_token": access_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "朝のランニング"

    def test_未認証ユーザーはマイルストーン一覧を取得できないこと(self):
        """GET /api/v1/milestonesで未認証ユーザーは401エラーになること"""
        response = client.get("/api/v1/milestones")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_認証済みユーザーはマイルストーンを更新できること(self):
        """PUT /api/v1/milestones/{milestone_id}で認証済みユーザーはマイルストーンを更新できること"""
        user, access_token = self._create_authenticated_user()

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

        create_response = client.post(
            "/api/v1/milestones",
            json=milestone_data,
            cookies={"access_token": access_token},
        )
        milestone_id = create_response.json()["id"]

        # マイルストーンを更新
        update_data = {"title": "朝のジョギング"}

        response = client.put(
            f"/api/v1/milestones/{milestone_id}",
            json=update_data,
            cookies={"access_token": access_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "朝のジョギング"

    def test_認証済みユーザーはマイルストーンを削除できること(self):
        """DELETE /api/v1/milestones/{milestone_id}で認証済みユーザーはマイルストーンを削除できること"""
        user, access_token = self._create_authenticated_user()

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

        create_response = client.post(
            "/api/v1/milestones",
            json=milestone_data,
            cookies={"access_token": access_token},
        )
        milestone_id = create_response.json()["id"]

        # マイルストーンを削除
        response = client.delete(
            f"/api/v1/milestones/{milestone_id}",
            cookies={"access_token": access_token},
        )

        assert response.status_code == 200

        # 一覧取得で確認
        list_response = client.get(
            "/api/v1/milestones", cookies={"access_token": access_token}
        )
        assert len(list_response.json()) == 0
