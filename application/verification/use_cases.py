"""Verification use cases"""

from uuid import UUID
from pydantic import BaseModel, Field
from domain.achievement.models import AchievementRecord
from domain.achievement.repositories import AchievementRepository
from domain.milestone.models import MilestoneId
from domain.milestone.repositories import MilestoneRepository
from domain.shared.exceptions import UnauthorizedError
from domain.user.models import UserId
from domain.verification.models import Verification, Location
from domain.verification.repositories import VerificationRepository
from domain.verification.services import GPSVerificationService
from infrastructure.shared.result import Result, Ok, Err


class StartVerificationInput(BaseModel):
    """Input for starting a verification"""

    milestone_id: str = Field(..., description="Milestone ID")
    user_id: str = Field(..., description="User ID")


class SubmitLocationInput(BaseModel):
    """Input for submitting location data"""

    verification_id: str = Field(..., description="Verification ID")
    user_id: str = Field(..., description="User ID")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    accuracy: float | None = Field(default=None, description="Accuracy (meters)")


class CompleteVerificationInput(BaseModel):
    """Input for completing a verification"""

    verification_id: str = Field(..., description="Verification ID")
    user_id: str = Field(..., description="User ID")


class StartVerificationUseCase:
    """Start verification use case"""

    def __init__(
        self,
        milestone_repository: MilestoneRepository,
        verification_repository: VerificationRepository,
    ) -> None:
        self._milestone_repository = milestone_repository
        self._verification_repository = verification_repository

    async def execute(
        self, input_data: StartVerificationInput
    ) -> Result[Verification, Exception]:
        """Run the start verification flow"""
        milestone_id = MilestoneId(value=UUID(input_data.milestone_id))
        milestone_result = await self._milestone_repository.find_by_id(milestone_id)
        if milestone_result.is_err():
            return Err(Exception("Milestone not found"))

        milestone = milestone_result.unwrap()

        user_id = UserId(value=UUID(input_data.user_id))
        if milestone.user_id.value != user_id.value:
            return Err(
                UnauthorizedError("You are not authorized to start this verification")
            )

        verification = Verification.create(
            milestone_id=milestone.id.value, user_id=user_id.value
        )
        save_result = await self._verification_repository.save(verification)
        if save_result.is_err():
            return Err(Exception("Failed to save verification"))

        return Ok(verification)


class SubmitLocationUseCase:
    """Submit location use case"""

    def __init__(self, verification_repository: VerificationRepository) -> None:
        self._verification_repository = verification_repository

    async def execute(
        self, input_data: SubmitLocationInput
    ) -> Result[Verification, Exception]:
        """Run the submit location flow"""
        verification_result = await self._verification_repository.find_by_id(
            UUID(input_data.verification_id)
        )
        if verification_result.is_err():
            return Err(Exception("Verification not found"))

        verification = verification_result.unwrap()

        user_id = UserId(value=UUID(input_data.user_id))
        if verification.user_id != user_id.value:
            return Err(
                UnauthorizedError("You are not authorized to submit location data")
            )

        location = Location(
            latitude=input_data.latitude, longitude=input_data.longitude
        )
        updated = verification.submit_location(location, accuracy=input_data.accuracy)
        save_result = await self._verification_repository.save(updated)
        if save_result.is_err():
            return Err(Exception("Failed to save verification"))

        return Ok(updated)


class CompleteVerificationUseCase:
    """Complete verification use case"""

    def __init__(
        self,
        milestone_repository: MilestoneRepository,
        verification_repository: VerificationRepository,
        achievement_repository: AchievementRepository,
    ) -> None:
        self._milestone_repository = milestone_repository
        self._verification_repository = verification_repository
        self._achievement_repository = achievement_repository

    async def execute(
        self, input_data: CompleteVerificationInput
    ) -> Result[tuple[Verification, AchievementRecord], Exception]:
        """Run the complete verification flow"""
        verification_result = await self._verification_repository.find_by_id(
            UUID(input_data.verification_id)
        )
        if verification_result.is_err():
            return Err(Exception("Verification not found"))

        verification = verification_result.unwrap()

        user_id = UserId(value=UUID(input_data.user_id))
        if verification.user_id != user_id.value:
            return Err(
                UnauthorizedError("You are not authorized to complete this verification")
            )

        milestone_result = await self._milestone_repository.find_by_id(
            MilestoneId(value=verification.milestone_id)
        )
        if milestone_result.is_err():
            return Err(Exception("Milestone not found"))

        milestone = milestone_result.unwrap()

        if len(verification.sensor_data) == 0:
            failed_verification = verification.fail("No sensor data")
            save_result = await self._verification_repository.save(failed_verification)
            if save_result.is_err():
                return Err(Exception("Failed to save verification"))

            achievement = AchievementRecord.record_failure(
                milestone.id.value, verification.user_id, "No sensor data"
            )
            achievement_result = await self._achievement_repository.save(achievement)
            if achievement_result.is_err():
                return Err(Exception("Failed to save achievement"))

            return Ok((failed_verification, achievement))

        last_sensor = verification.sensor_data[-1]
        result = GPSVerificationService.verify(
            last_sensor.location, milestone.verification_criteria
        )

        completed_verification = verification.complete(result)
        save_result = await self._verification_repository.save(completed_verification)
        if save_result.is_err():
            return Err(Exception("Failed to save verification"))

        if result.success:
            achievement = AchievementRecord.record_achievement(
                milestone.id.value,
                verification.user_id,
                verification.id,
                result.score,
            )
        else:
            achievement = AchievementRecord.record_failure(
                milestone.id.value,
                verification.user_id,
                f"Distance: {result.evidence['distance_meters']}m",
            )

        achievement_result = await self._achievement_repository.save(achievement)
        if achievement_result.is_err():
            return Err(Exception("Failed to save achievement"))

        updated_milestone = milestone.complete() if result.success else milestone.fail()
        milestone_save_result = await self._milestone_repository.save(updated_milestone)
        if milestone_save_result.is_err():
            return Err(Exception("Failed to save milestone"))

        return Ok((completed_verification, achievement))
