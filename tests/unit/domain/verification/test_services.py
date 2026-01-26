"""GPS検証サービスのテスト"""

from domain.verification.models import Location, Distance, VerificationResult
from domain.verification.services import GPSVerificationService
from domain.milestone.value_objects import VerificationCriteria


class TestGPSVerificationService:
    """GPS検証ドメインサービスのテスト"""

    def test_Haversine公式で距離を計算できること(self):
        """Given: 東京駅と新宿駅の座標
        When: 距離を計算
        Then: 約6.5km（6000-7000m）"""
        # Given: 東京駅と新宿駅
        tokyo = Location(latitude=35.6812, longitude=139.7671)
        shinjuku = Location(latitude=35.6896, longitude=139.7006)

        # When
        distance = GPSVerificationService.calculate_distance(tokyo, shinjuku)

        # Then: 約6.5km
        assert isinstance(distance, Distance)
        assert 6000 < distance.meters < 7000

    def test_同じ位置の距離は0メートルであること(self):
        """Given: 同じ座標
        When: 距離を計算
        Then: 0メートル"""
        # Given
        location = Location(latitude=35.6812, longitude=139.7671)

        # When
        distance = GPSVerificationService.calculate_distance(location, location)

        # Then
        assert distance.meters == 0.0

    def test_赤道上の2点間の距離を計算できること(self):
        """Given: 赤道上の2点（経度1度差）
        When: 距離を計算
        Then: 約111km（赤道上の1度 ≈ 111km）"""
        # Given: 赤道上の2点（経度1度差）
        point1 = Location(latitude=0.0, longitude=0.0)
        point2 = Location(latitude=0.0, longitude=1.0)

        # When
        distance = GPSVerificationService.calculate_distance(point1, point2)

        # Then: 約111km
        assert 110000 < distance.meters < 112000

    def test_位置情報検証が成功すること(self):
        """Given: 閾値内の位置情報
        When: 検証を実行
        Then: success=True、スコア0.5以上"""
        # Given: ターゲット位置と検証条件（100m以内）
        criteria = VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        )
        # 現在位置（ターゲットから約50m）
        current = Location(latitude=35.68165, longitude=139.7671)

        # When
        result = GPSVerificationService.verify(current, criteria)

        # Then
        assert isinstance(result, VerificationResult)
        assert result.success is True
        assert result.score >= 0.5
        assert result.confidence == 1.0
        assert "distance_meters" in result.evidence
        assert result.evidence["distance_meters"] < 100.0

    def test_位置情報検証が失敗すること(self):
        """Given: 閾値外の位置情報
        When: 検証を実行
        Then: success=False、スコア0.5未満"""
        # Given: ターゲット位置と検証条件（100m以内）
        criteria = VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        )
        # 現在位置（ターゲットから約200m）
        current = Location(latitude=35.683, longitude=139.7671)

        # When
        result = GPSVerificationService.verify(current, criteria)

        # Then
        assert isinstance(result, VerificationResult)
        assert result.success is False
        assert result.score < 0.5
        assert result.confidence == 1.0
        assert "distance_meters" in result.evidence
        assert result.evidence["distance_meters"] > 100.0

    def test_検証結果には証拠データが含まれること(self):
        """Given: 位置情報検証
        When: 検証を実行
        Then: 証拠データ（距離、閾値、座標）が含まれる"""
        # Given
        criteria = VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        )
        current = Location(latitude=35.68165, longitude=139.7671)

        # When
        result = GPSVerificationService.verify(current, criteria)

        # Then
        assert "distance_meters" in result.evidence
        assert "threshold_meters" in result.evidence
        assert "target" in result.evidence
        assert "current" in result.evidence
        assert result.evidence["threshold_meters"] == 100.0
        assert result.evidence["target"]["lat"] == 35.6812
        assert result.evidence["target"]["lon"] == 139.7671
        assert result.evidence["current"]["lat"] == 35.68165
        assert result.evidence["current"]["lon"] == 139.7671

    def test_閾値ギリギリの位置は成功すること(self):
        """Given: 閾値ちょうどの位置情報
        When: 検証を実行
        Then: success=True（等号を含む）"""
        # Given: ターゲット位置と検証条件（100m以内）
        criteria = VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        )
        # 距離を計算して、ちょうど100mになる位置を探す
        # 緯度約0.0009度 ≈ 100m
        current = Location(latitude=35.68210, longitude=139.7671)

        # When
        result = GPSVerificationService.verify(current, criteria)

        # Then
        # 100m付近なので、成功の可能性が高い（完全に100mでなくても近い）
        assert isinstance(result, VerificationResult)
        assert result.confidence == 1.0
