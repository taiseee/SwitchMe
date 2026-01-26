"""検証ドメインモデル"""

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Literal, Any


class Location(BaseModel):
    """位置情報（値オブジェクト）

    緯度経度で位置を表現する。
    """

    model_config = {"frozen": True}

    latitude: float = Field(..., ge=-90, le=90, description="緯度（-90〜90度）")
    longitude: float = Field(..., ge=-180, le=180, description="経度（-180〜180度）")


class Distance(BaseModel):
    """距離（値オブジェクト）

    メートル単位で距離を表現する。
    """

    model_config = {"frozen": True}

    meters: float = Field(..., ge=0, description="距離（メートル）")


class VerificationResult(BaseModel):
    """検証結果（値オブジェクト）

    検証の成否、スコア、信頼度、証拠を保持する。
    """

    model_config = {"frozen": True}

    success: bool = Field(..., description="検証成功フラグ")
    score: float = Field(..., ge=0, le=1, description="検証スコア（0〜1）")
    confidence: float = Field(..., ge=0, le=1, description="信頼度（0〜1）")
    evidence: dict[str, Any] = Field(..., description="検証の証拠データ")


class SensorData(BaseModel):
    """センサーデータ（エンティティ）

    位置情報センサーから取得したデータを表現する。
    """

    id: UUID = Field(default_factory=uuid4, description="センサーデータID")
    location: Location = Field(..., description="位置情報")
    timestamp: datetime = Field(..., description="タイムスタンプ")
    accuracy: float | None = Field(None, description="精度（メートル）")


VerificationStatus = Literal["pending", "in_progress", "completed", "failed"]


class Verification(BaseModel):
    """検証プロセス（集約ルート）

    マイルストーンの検証プロセス全体を管理する。
    センサーデータの収集、検証の実行、結果の記録を行う。
    """

    model_config = {"frozen": True}

    id: UUID = Field(..., description="検証ID")
    milestone_id: UUID = Field(..., description="マイルストーンID")
    user_id: UUID = Field(..., description="ユーザーID")
    status: VerificationStatus = Field(..., description="検証ステータス")
    sensor_data: list[SensorData] = Field(
        default_factory=list, description="センサーデータリスト"
    )
    result: VerificationResult | None = Field(None, description="検証結果")
    started_at: datetime = Field(..., description="検証開始日時")
    completed_at: datetime | None = Field(None, description="検証完了日時")

    @classmethod
    def create(cls, milestone_id: UUID, user_id: UUID) -> "Verification":
        """検証プロセスを開始する

        Args:
            milestone_id: マイルストーンID
            user_id: ユーザーID

        Returns:
            新しいVerificationインスタンス（pending状態）
        """
        return cls(
            id=uuid4(),
            milestone_id=milestone_id,
            user_id=user_id,
            status="pending",
            started_at=datetime.now(timezone.utc),
        )

    def submit_location(
        self, location: Location, accuracy: float | None = None
    ) -> "Verification":
        """位置情報を送信する

        Args:
            location: 位置情報
            accuracy: 精度（メートル）

        Returns:
            位置情報が追加された新しいVerificationインスタンス
        """
        sensor = SensorData(
            location=location, timestamp=datetime.now(timezone.utc), accuracy=accuracy
        )
        return self.model_copy(
            update={
                "sensor_data": [*self.sensor_data, sensor],
                "status": "in_progress",
            }
        )

    def complete(self, result: VerificationResult) -> "Verification":
        """検証を完了する

        Args:
            result: 検証結果

        Returns:
            検証完了した新しいVerificationインスタンス
        """
        return self.model_copy(
            update={
                "result": result,
                "status": "completed",
                "completed_at": datetime.now(timezone.utc),
            }
        )

    def fail(self, reason: str) -> "Verification":
        """検証を失敗にする

        Args:
            reason: 失敗理由

        Returns:
            検証失敗した新しいVerificationインスタンス
        """
        result = VerificationResult(
            success=False, score=0.0, confidence=1.0, evidence={"reason": reason}
        )
        return self.model_copy(
            update={
                "result": result,
                "status": "failed",
                "completed_at": datetime.now(timezone.utc),
            }
        )
