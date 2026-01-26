"""Verification API integration tests"""

from datetime import date, time
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app
from apps.api.dependencies import _token_manager
from domain.user.models import User, Email, OAuthProvider
from domain.milestone.models import Milestone, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.value_objects import Money
from infrastructure.shared.database import get_session_maker
from infrastructure.user.persistence.repository import PostgresUserRepository
from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository


class TestVerificationAPI:
    """Verification API integration tests"""

    async def _create_authenticated_user_and_milestone(
        self, target_lat: float = 35.6812, target_lon: float = 139.7671
    ):
        """Create an authenticated user and milestone"""
        user = User.create(
            email=Email(value="test@example.com"),
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="google_user_123",
        )
        milestone = Milestone.create(
            user_id=user.id,
            title=Title(value="Morning run"),
            deadline=DeadlineInfo(
                date=date(2026, 1, 27), time=time(7, 0), timezone="Asia/Tokyo"
            ),
            verification_criteria=VerificationCriteria(
                type="location",
                conditions={"lat": target_lat, "lon": target_lon},
                threshold=100.0,
            ),
            penalty=PenaltyInfo(
                amount=Money(amount=1000, currency="JPY"), description="Penalty"
            ),
        )

        session_maker = get_session_maker()
        async with session_maker() as session:
            user_repo = PostgresUserRepository(session)
            milestone_repo = PostgresMilestoneRepository(session)
            await user_repo.save(user)
            await milestone_repo.save(milestone)

        access_token = _token_manager.create_access_token(
            str(user.id.value), user.email.value
        )
        return user, milestone, access_token

    @pytest.mark.anyio
    async def test_start_to_complete_flow_succeeds(self):
        """Start -> submit location -> complete flow succeeds"""
        _, milestone, access_token = await self._create_authenticated_user_and_milestone()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            start_response = await client.post(
                "/api/v1/verifications",
                json={"milestone_id": str(milestone.id.value)},
                cookies={"access_token": access_token},
            )

            assert start_response.status_code == 201
            start_data = start_response.json()
            verification_id = start_data["id"]
            assert start_data["status"] == "pending"

            location_response = await client.post(
                f"/api/v1/verifications/{verification_id}/location",
                json={"latitude": 35.6812, "longitude": 139.7671},
                cookies={"access_token": access_token},
            )

            assert location_response.status_code == 200
            location_data = location_response.json()
            assert location_data["status"] == "in_progress"
            assert len(location_data["sensor_data"]) == 1

            complete_response = await client.post(
                f"/api/v1/verifications/{verification_id}/complete",
                cookies={"access_token": access_token},
            )

            assert complete_response.status_code == 200
            complete_data = complete_response.json()
            assert complete_data["verification"]["status"] == "completed"
            assert complete_data["verification"]["result"]["success"] is True
            assert complete_data["achievement"]["status"]["achieved"] is True
            assert complete_data["achievement"]["evidence"]["type"] == "verification"

    @pytest.mark.anyio
    async def test_location_too_far_fails(self):
        """Far location should fail verification"""
        _, milestone, access_token = await self._create_authenticated_user_and_milestone()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            start_response = await client.post(
                "/api/v1/verifications",
                json={"milestone_id": str(milestone.id.value)},
                cookies={"access_token": access_token},
            )

            assert start_response.status_code == 201
            verification_id = start_response.json()["id"]

            location_response = await client.post(
                f"/api/v1/verifications/{verification_id}/location",
                json={"latitude": 0.0, "longitude": 0.0},
                cookies={"access_token": access_token},
            )

            assert location_response.status_code == 200
            complete_response = await client.post(
                f"/api/v1/verifications/{verification_id}/complete",
                cookies={"access_token": access_token},
            )

            assert complete_response.status_code == 200
            complete_data = complete_response.json()
            assert complete_data["verification"]["result"]["success"] is False
            assert complete_data["achievement"]["status"]["achieved"] is False
            assert complete_data["achievement"]["status"]["reason"].startswith("Distance:")
