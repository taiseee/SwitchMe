"""検証ドメインモデルのテスト"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from domain.verification.models import (
    Location,
    Distance,
    VerificationResult,
    SensorData,
    Verification,
)


class TestLocation:
    """Location値オブジェクトのテスト"""

    def test_位置情報値オブジェクトが作成できること(self):
        """Given: 有効な緯度経度
        When: Locationを作成
        Then: 正常に作成される"""
        # When
        location = Location(latitude=35.6812, longitude=139.7671)

        # Then
        assert location.latitude == 35.6812
        assert location.longitude == 139.7671

    def test_無効な緯度は拒否されること(self):
        """Given: 範囲外の緯度（-90〜90度外）
        When: Locationを作成
        Then: バリデーションエラー"""
        # When/Then
        with pytest.raises(Exception):
            Location(latitude=91.0, longitude=139.7671)

        with pytest.raises(Exception):
            Location(latitude=-91.0, longitude=139.7671)

    def test_無効な経度は拒否されること(self):
        """Given: 範囲外の経度（-180〜180度外）
        When: Locationを作成
        Then: バリデーションエラー"""
        # When/Then
        with pytest.raises(Exception):
            Location(latitude=35.6812, longitude=181.0)

        with pytest.raises(Exception):
            Location(latitude=35.6812, longitude=-181.0)

    def test_Locationは不変であること(self):
        """Given: Location
        When: 属性を変更しようとする
        Then: エラーが発生する"""
        # Given
        location = Location(latitude=35.6812, longitude=139.7671)

        # When/Then
        with pytest.raises(Exception):
            location.latitude = 40.0  # type: ignore


class TestDistance:
    """Distance値オブジェクトのテスト"""

    def test_距離が作成できること(self):
        """Given: 正の距離
        When: Distanceを作成
        Then: 正常に作成される"""
        # When
        distance = Distance(meters=1000.5)

        # Then
        assert distance.meters == 1000.5

    def test_負の距離は拒否されること(self):
        """Given: 負の距離
        When: Distanceを作成
        Then: バリデーションエラー"""
        # When/Then
        with pytest.raises(Exception):
            Distance(meters=-1.0)


class TestVerificationResult:
    """VerificationResult値オブジェクトのテスト"""

    def test_検証結果が作成できること(self):
        """Given: 検証結果データ
        When: VerificationResultを作成
        Then: 正常に作成される"""
        # When
        result = VerificationResult(
            success=True,
            score=0.95,
            confidence=1.0,
            evidence={"distance_meters": 50.0, "threshold_meters": 100.0},
        )

        # Then
        assert result.success is True
        assert result.score == 0.95
        assert result.confidence == 1.0
        assert result.evidence["distance_meters"] == 50.0

    def test_スコアは0から1の範囲であること(self):
        """Given: 範囲外のスコア
        When: VerificationResultを作成
        Then: バリデーションエラー"""
        # When/Then
        with pytest.raises(Exception):
            VerificationResult(success=True, score=1.5, confidence=1.0, evidence={})

        with pytest.raises(Exception):
            VerificationResult(success=True, score=-0.5, confidence=1.0, evidence={})


class TestSensorData:
    """SensorDataエンティティのテスト"""

    def test_センサーデータが作成できること(self):
        """Given: 位置情報とタイムスタンプ
        When: SensorDataを作成
        Then: 正常に作成される"""
        # Given
        location = Location(latitude=35.6812, longitude=139.7671)
        timestamp = datetime.now(timezone.utc)

        # When
        sensor = SensorData(location=location, timestamp=timestamp, accuracy=10.5)

        # Then
        assert sensor.location == location
        assert sensor.timestamp == timestamp
        assert sensor.accuracy == 10.5


class TestVerification:
    """Verification集約ルートのテスト"""

    def test_検証を開始できること(self):
        """Given: マイルストーンIDとユーザーID
        When: Verificationを作成
        Then: pending状態で作成される"""
        # Given
        milestone_id = uuid4()
        user_id = uuid4()

        # When
        verification = Verification.create(milestone_id=milestone_id, user_id=user_id)

        # Then
        assert verification.milestone_id == milestone_id
        assert verification.user_id == user_id
        assert verification.status == "pending"
        assert len(verification.sensor_data) == 0
        assert verification.result is None

    def test_位置情報データを記録できること(self):
        """Given: 作成済みVerification
        When: 位置情報を送信
        Then: センサーデータが追加され、ステータスがin_progressになる"""
        # Given
        verification = Verification.create(milestone_id=uuid4(), user_id=uuid4())
        location = Location(latitude=35.6812, longitude=139.7671)

        # When
        updated = verification.submit_location(location, accuracy=5.0)

        # Then
        assert updated.status == "in_progress"
        assert len(updated.sensor_data) == 1
        assert updated.sensor_data[0].location == location
        assert updated.sensor_data[0].accuracy == 5.0

    def test_複数の位置情報を記録できること(self):
        """Given: 作成済みVerification
        When: 複数回位置情報を送信
        Then: 複数のセンサーデータが記録される"""
        # Given
        verification = Verification.create(milestone_id=uuid4(), user_id=uuid4())
        location1 = Location(latitude=35.6812, longitude=139.7671)
        location2 = Location(latitude=35.6896, longitude=139.7006)

        # When
        updated1 = verification.submit_location(location1)
        updated2 = updated1.submit_location(location2)

        # Then
        assert len(updated2.sensor_data) == 2
        assert updated2.sensor_data[0].location == location1
        assert updated2.sensor_data[1].location == location2

    def test_検証を完了できること(self):
        """Given: 位置情報送信済みVerification
        When: 検証を完了
        Then: ステータスがcompletedになり、結果が保存される"""
        # Given
        verification = Verification.create(milestone_id=uuid4(), user_id=uuid4())
        verification = verification.submit_location(
            Location(latitude=35.6812, longitude=139.7671)
        )
        result = VerificationResult(
            success=True, score=0.95, confidence=1.0, evidence={}
        )

        # When
        completed = verification.complete(result)

        # Then
        assert completed.status == "completed"
        assert completed.result == result
        assert completed.completed_at is not None

    def test_検証を失敗にできること(self):
        """Given: Verification
        When: 検証を失敗
        Then: ステータスがfailedになり、失敗理由が保存される"""
        # Given
        verification = Verification.create(milestone_id=uuid4(), user_id=uuid4())

        # When
        failed = verification.fail("No sensor data")

        # Then
        assert failed.status == "failed"
        assert failed.result is not None
        assert failed.result.success is False
        assert failed.result.evidence["reason"] == "No sensor data"
        assert failed.completed_at is not None

    def test_Verificationは不変であること(self):
        """Given: Verification
        When: メソッド呼び出し
        Then: 新しいインスタンスが返される（元は変更されない）"""
        # Given
        verification = Verification.create(milestone_id=uuid4(), user_id=uuid4())
        original_status = verification.status

        # When
        updated = verification.submit_location(
            Location(latitude=35.6812, longitude=139.7671)
        )

        # Then
        assert verification.status == original_status  # 元は変更されない
        assert updated.status == "in_progress"  # 新しいインスタンスは変更されている
        assert verification.id == updated.id  # IDは同じ
