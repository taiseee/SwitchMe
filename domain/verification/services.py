"""GPS検証ドメインサービス"""

import math
from domain.verification.models import Location, Distance, VerificationResult
from domain.milestone.value_objects import VerificationCriteria


class GPSVerificationService:
    """GPS検証ドメインサービス

    Haversine公式を使用した距離計算と位置情報検証を提供する。
    """

    EARTH_RADIUS_METERS = 6371000  # 地球の半径（メートル）

    @staticmethod
    def calculate_distance(loc1: Location, loc2: Location) -> Distance:
        """Haversine公式で2点間の距離を計算

        Args:
            loc1: 地点1
            loc2: 地点2

        Returns:
            2点間の距離（メートル）
        """
        # 度数法からラジアンに変換
        lat1 = math.radians(loc1.latitude)
        lat2 = math.radians(loc2.latitude)
        delta_lat = math.radians(loc2.latitude - loc1.latitude)
        delta_lon = math.radians(loc2.longitude - loc1.longitude)

        # Haversine公式
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        meters = GPSVerificationService.EARTH_RADIUS_METERS * c

        return Distance(meters=meters)

    @staticmethod
    def verify(
        current_location: Location, criteria: VerificationCriteria
    ) -> VerificationResult:
        """位置情報を検証

        Args:
            current_location: 現在位置
            criteria: 検証条件

        Returns:
            検証結果
        """
        # ターゲット位置を取得
        target = Location(
            latitude=criteria.conditions["lat"], longitude=criteria.conditions["lon"]
        )

        # 距離を計算
        distance = GPSVerificationService.calculate_distance(current_location, target)

        # 成功判定（閾値以内）
        success = distance.meters <= criteria.threshold

        # スコア計算
        # - 閾値内: スコア 0.5〜1.0（距離が近いほど高い）
        # - 閾値外: スコア 0.0〜0.5（距離が遠いほど低い）
        if distance.meters <= criteria.threshold:
            # 閾値内: 1.0 - (距離 / 閾値) * 0.5
            # 距離0m → スコア1.0、距離=閾値 → スコア0.5
            score = 1.0 - (distance.meters / criteria.threshold) * 0.5
        else:
            # 閾値外: 0.5 - (超過距離 / 閾値) * 0.5
            # 距離=閾値 → スコア0.5、距離=閾値*2 → スコア0.0
            score = max(
                0.0,
                0.5 - (distance.meters - criteria.threshold) / criteria.threshold * 0.5,
            )

        # 証拠データ
        evidence = {
            "distance_meters": distance.meters,
            "threshold_meters": criteria.threshold,
            "target": {"lat": target.latitude, "lon": target.longitude},
            "current": {
                "lat": current_location.latitude,
                "lon": current_location.longitude,
            },
        }

        return VerificationResult(
            success=success, score=score, confidence=1.0, evidence=evidence
        )
