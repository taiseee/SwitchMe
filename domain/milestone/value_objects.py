"""Milestone値オブジェクト"""

from datetime import datetime, date, time, timezone as tz
from typing import Literal, Any
from pydantic import BaseModel, Field
from domain.shared.value_objects import Money


VerificationType = Literal["location", "image", "audio"]


class DeadlineInfo(BaseModel):
    """期限情報（値オブジェクト）

    マイルストーンの期限に関する情報を保持する。
    """

    model_config = {"frozen": True}

    deadline_date: date = Field(..., description="期限日", alias="date")
    deadline_time: time = Field(..., description="期限時刻", alias="time")
    timezone: str = Field(..., description="タイムゾーン（例: Asia/Tokyo）")

    def to_datetime(self) -> datetime:
        """期限をdatetimeオブジェクトに変換する

        Returns:
            期限のdatetimeオブジェクト
        """
        # タイムゾーンを考慮したdatetimeを作成
        dt = datetime.combine(self.deadline_date, self.deadline_time)
        # 簡易実装：タイムゾーン情報はUTCとして扱う
        return dt.replace(tzinfo=tz.utc)


class VerificationCriteria(BaseModel):
    """検証基準（値オブジェクト）

    マイルストーンの達成を検証するための基準。
    """

    model_config = {"frozen": True}

    type: VerificationType = Field(..., description="検証タイプ")
    conditions: dict[str, Any] = Field(..., description="検証条件")
    threshold: float = Field(..., description="検証閾値")


class PenaltyInfo(BaseModel):
    """ペナルティ情報（値オブジェクト）

    未達成時のペナルティに関する情報。
    """

    model_config = {"frozen": True}

    amount: Money = Field(..., description="ペナルティ金額")
    description: str = Field(default="", description="ペナルティの説明")
