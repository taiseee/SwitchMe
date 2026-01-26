"""Verification API router"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from domain.user.models import User
from domain.verification.models import Verification, SensorData
from domain.achievement.models import AchievementRecord
from application.verification.use_cases import (
    StartVerificationInput,
    StartVerificationUseCase,
    SubmitLocationInput,
    SubmitLocationUseCase,
    CompleteVerificationInput,
    CompleteVerificationUseCase,
)
from apps.api.dependencies import (
    get_current_user,
    get_milestone_repository,
    get_verification_repository,
    get_achievement_repository,
)

router = APIRouter(prefix="/verifications", tags=["verifications"])


class StartVerificationRequest(BaseModel):
    """Start verification request"""

    milestone_id: str = Field(..., description="Milestone ID")


class SubmitLocationRequest(BaseModel):
    """Submit location request"""

    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    accuracy: float | None = Field(default=None, description="Accuracy (meters)")


class SensorDataResponse(BaseModel):
    """Sensor data response"""

    id: str = Field(..., description="Sensor data ID")
    location: dict[str, float] = Field(..., description="Location")
    timestamp: str = Field(..., description="Timestamp")
    accuracy: float | None = Field(None, description="Accuracy (meters)")


class VerificationResultResponse(BaseModel):
    """Verification result response"""

    success: bool = Field(..., description="Success flag")
    score: float = Field(..., description="Verification score")
    confidence: float = Field(..., description="Confidence")
    evidence: dict[str, Any] = Field(..., description="Evidence")


class VerificationResponse(BaseModel):
    """Verification response"""

    id: str = Field(..., description="Verification ID")
    milestone_id: str = Field(..., description="Milestone ID")
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Status")
    sensor_data: list[SensorDataResponse] = Field(..., description="Sensor data")
    result: VerificationResultResponse | None = Field(None, description="Result")
    started_at: str = Field(..., description="Started at")
    completed_at: str | None = Field(None, description="Completed at")


class AchievementStatusResponse(BaseModel):
    """Achievement status response"""

    achieved: bool = Field(..., description="Achieved flag")
    score: float = Field(..., description="Score")
    reason: str = Field(..., description="Reason")


class EvidenceResponse(BaseModel):
    """Evidence response"""

    type: str = Field(..., description="Evidence type")
    references: list[str] = Field(..., description="Reference IDs")
    metadata: dict[str, Any] = Field(..., description="Metadata")


class AchievementResponse(BaseModel):
    """Achievement response"""

    id: str = Field(..., description="Achievement ID")
    milestone_id: str = Field(..., description="Milestone ID")
    user_id: str = Field(..., description="User ID")
    status: AchievementStatusResponse = Field(..., description="Status")
    evidence: EvidenceResponse = Field(..., description="Evidence")
    recorded_at: str = Field(..., description="Recorded at")


class CompleteVerificationResponse(BaseModel):
    """Complete verification response"""

    verification: VerificationResponse = Field(..., description="Verification")
    achievement: AchievementResponse = Field(..., description="Achievement")


def _sensor_data_to_response(sensor: SensorData) -> SensorDataResponse:
    """Convert SensorData to SensorDataResponse"""
    return SensorDataResponse(
        id=str(sensor.id),
        location={
            "latitude": sensor.location.latitude,
            "longitude": sensor.location.longitude,
        },
        timestamp=sensor.timestamp.isoformat(),
        accuracy=sensor.accuracy,
    )


def _verification_to_response(verification: Verification) -> VerificationResponse:
    """Convert Verification to VerificationResponse"""
    result = None
    if verification.result is not None:
        result = VerificationResultResponse(
            success=verification.result.success,
            score=verification.result.score,
            confidence=verification.result.confidence,
            evidence=verification.result.evidence,
        )

    return VerificationResponse(
        id=str(verification.id),
        milestone_id=str(verification.milestone_id),
        user_id=str(verification.user_id),
        status=verification.status,
        sensor_data=[_sensor_data_to_response(s) for s in verification.sensor_data],
        result=result,
        started_at=verification.started_at.isoformat(),
        completed_at=(
            verification.completed_at.isoformat()
            if verification.completed_at
            else None
        ),
    )


def _achievement_to_response(achievement: AchievementRecord) -> AchievementResponse:
    """Convert AchievementRecord to AchievementResponse"""
    return AchievementResponse(
        id=str(achievement.id),
        milestone_id=str(achievement.milestone_id),
        user_id=str(achievement.user_id),
        status=AchievementStatusResponse(
            achieved=achievement.status.achieved,
            score=achievement.status.score,
            reason=achievement.status.reason,
        ),
        evidence=EvidenceResponse(
            type=achievement.evidence.type,
            references=[str(ref) for ref in achievement.evidence.references],
            metadata=achievement.evidence.metadata,
        ),
        recorded_at=achievement.recorded_at.isoformat(),
    )


@router.post("", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def start_verification(
    request: StartVerificationRequest,
    current_user: User = Depends(get_current_user),
    milestone_repository=Depends(get_milestone_repository),
    verification_repository=Depends(get_verification_repository),
):
    """Start a verification"""
    use_case = StartVerificationUseCase(
        milestone_repository, verification_repository
    )
    input_data = StartVerificationInput(
        milestone_id=request.milestone_id, user_id=str(current_user.id.value)
    )
    result = await use_case.execute(input_data)

    if result.is_err():
        error = result.unwrap_err()
        if "not authorized" in str(error).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return _verification_to_response(result.unwrap())


@router.post("/{verification_id}/location", response_model=VerificationResponse)
async def submit_location(
    verification_id: str,
    request: SubmitLocationRequest,
    current_user: User = Depends(get_current_user),
    verification_repository=Depends(get_verification_repository),
):
    """Submit location data"""
    use_case = SubmitLocationUseCase(verification_repository)
    input_data = SubmitLocationInput(
        verification_id=verification_id,
        user_id=str(current_user.id.value),
        latitude=request.latitude,
        longitude=request.longitude,
        accuracy=request.accuracy,
    )
    result = await use_case.execute(input_data)

    if result.is_err():
        error = result.unwrap_err()
        if "not authorized" in str(error).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return _verification_to_response(result.unwrap())


@router.post("/{verification_id}/complete", response_model=CompleteVerificationResponse)
async def complete_verification(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    milestone_repository=Depends(get_milestone_repository),
    verification_repository=Depends(get_verification_repository),
    achievement_repository=Depends(get_achievement_repository),
):
    """Complete a verification"""
    use_case = CompleteVerificationUseCase(
        milestone_repository, verification_repository, achievement_repository
    )
    input_data = CompleteVerificationInput(
        verification_id=verification_id, user_id=str(current_user.id.value)
    )
    result = await use_case.execute(input_data)

    if result.is_err():
        error = result.unwrap_err()
        if "not authorized" in str(error).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    verification, achievement = result.unwrap()
    return CompleteVerificationResponse(
        verification=_verification_to_response(verification),
        achievement=_achievement_to_response(achievement),
    )
