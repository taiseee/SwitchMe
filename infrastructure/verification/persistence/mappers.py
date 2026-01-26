"""Verification マッパー"""

from domain.verification.models import (
    Verification,
    VerificationResult,
    SensorData,
    Location,
)
from infrastructure.shared.models import VerificationModel, SensorDataModel


def verification_to_orm(verification: Verification) -> VerificationModel:
    """ドメインモデル → ORMモデル

    Args:
        verification: 検証ドメインモデル

    Returns:
        検証ORMモデル
    """
    # VerificationResult → ORM (nullable)
    result_success = None
    result_score = None
    result_confidence = None
    result_evidence = None

    if verification.result is not None:
        result_success = verification.result.success
        result_score = verification.result.score
        result_confidence = verification.result.confidence
        result_evidence = verification.result.evidence

    return VerificationModel(
        id=verification.id,
        milestone_id=verification.milestone_id,
        user_id=verification.user_id,
        status=verification.status,
        result_success=result_success,
        result_score=result_score,
        result_confidence=result_confidence,
        result_evidence=result_evidence,
        started_at=verification.started_at,
        completed_at=verification.completed_at,
    )


def sensor_data_to_orm(sensor: SensorData, verification_id) -> SensorDataModel:
    """センサーデータドメインモデル → ORMモデル

    Args:
        sensor: センサーデータドメインモデル
        verification_id: 検証ID

    Returns:
        センサーデータORMモデル
    """
    return SensorDataModel(
        id=sensor.id,
        verification_id=verification_id,
        latitude=sensor.location.latitude,
        longitude=sensor.location.longitude,
        accuracy=sensor.accuracy,
        timestamp=sensor.timestamp,
    )


def orm_to_verification(
    model: VerificationModel,
) -> Verification:
    """ORMモデル → ドメインモデル

    Args:
        model: 検証ORMモデル

    Returns:
        検証ドメインモデル
    """
    # ORM → VerificationResult (nullable)
    result = None
    if model.result_success is not None:
        result = VerificationResult(
            success=model.result_success,
            score=model.result_score,
            confidence=model.result_confidence,
            evidence=model.result_evidence or {},
        )

    # SensorDataModel → SensorData
    sensor_data_list = [
        SensorData(
            id=sensor.id,
            location=Location(latitude=sensor.latitude, longitude=sensor.longitude),
            timestamp=sensor.timestamp,
            accuracy=sensor.accuracy,
        )
        for sensor in model.sensor_data
    ]

    return Verification(
        id=model.id,
        milestone_id=model.milestone_id,
        user_id=model.user_id,
        status=model.status,
        sensor_data=sensor_data_list,
        result=result,
        started_at=model.started_at,
        completed_at=model.completed_at,
    )
