"""達成記録ドメインモデルのテスト"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from domain.achievement.models import (
    AchievementStatus,
    Evidence,
    AchievementRecord,
)


class TestAchievementStatus:
    """AchievementStatus値オブジェクトのテスト"""

    def test_達成ステータスが作成できること(self):
        """Given: 達成情報
        When: AchievementStatusを作成
        Then: 正常に作成される"""
        # When
        status = AchievementStatus(achieved=True, score=0.95, reason="GPS検証成功")

        # Then
        assert status.achieved is True
        assert status.score == 0.95
        assert status.reason == "GPS検証成功"

    def test_未達成ステータスが作成できること(self):
        """Given: 未達成情報
        When: AchievementStatusを作成
        Then: 正常に作成される"""
        # When
        status = AchievementStatus(achieved=False, score=0.0, reason="距離超過")

        # Then
        assert status.achieved is False
        assert status.score == 0.0
        assert status.reason == "距離超過"

    def test_スコアは0から1の範囲であること(self):
        """Given: 範囲外のスコア
        When: AchievementStatusを作成
        Then: バリデーションエラー"""
        # When/Then
        with pytest.raises(Exception):
            AchievementStatus(achieved=True, score=1.5, reason="")

        with pytest.raises(Exception):
            AchievementStatus(achieved=True, score=-0.5, reason="")

    def test_AchievementStatusは不変であること(self):
        """Given: AchievementStatus
        When: 属性を変更しようとする
        Then: エラーが発生する"""
        # Given
        status = AchievementStatus(achieved=True, score=0.95, reason="成功")

        # When/Then
        with pytest.raises(Exception):
            status.achieved = False  # type: ignore


class TestEvidence:
    """Evidence値オブジェクトのテスト"""

    def test_検証タイプの証拠が作成できること(self):
        """Given: 検証参照
        When: Evidenceを作成
        Then: 正常に作成される"""
        # Given
        verification_id = uuid4()

        # When
        evidence = Evidence(type="verification", references=[verification_id])

        # Then
        assert evidence.type == "verification"
        assert len(evidence.references) == 1
        assert evidence.references[0] == verification_id

    def test_手動タイプの証拠が作成できること(self):
        """Given: メタデータ
        When: Evidenceを作成
        Then: 正常に作成される"""
        # When
        evidence = Evidence(
            type="manual", references=[], metadata={"reason": "手動で確認"}
        )

        # Then
        assert evidence.type == "manual"
        assert len(evidence.references) == 0
        assert evidence.metadata["reason"] == "手動で確認"

    def test_Evidenceは不変であること(self):
        """Given: Evidence
        When: 属性を変更しようとする
        Then: エラーが発生する"""
        # Given
        evidence = Evidence(type="verification", references=[])

        # When/Then
        with pytest.raises(Exception):
            evidence.type = "manual"  # type: ignore


class TestAchievementRecord:
    """AchievementRecord集約ルートのテスト"""

    def test_達成記録が作成できること(self):
        """Given: マイルストーンIDとユーザーID
        When: record_achievementで作成
        Then: 達成記録が作成される"""
        # Given
        milestone_id = uuid4()
        user_id = uuid4()
        verification_id = uuid4()

        # When
        record = AchievementRecord.record_achievement(
            milestone_id=milestone_id,
            user_id=user_id,
            verification_id=verification_id,
            score=0.95,
        )

        # Then
        assert record.milestone_id == milestone_id
        assert record.user_id == user_id
        assert record.status.achieved is True
        assert record.status.score == 0.95
        assert record.status.reason == "Verified by GPS"
        assert record.evidence.type == "verification"
        assert record.evidence.references == [verification_id]

    def test_失敗記録が作成できること(self):
        """Given: マイルストーンIDとユーザーID、失敗理由
        When: record_failureで作成
        Then: 失敗記録が作成される"""
        # Given
        milestone_id = uuid4()
        user_id = uuid4()

        # When
        record = AchievementRecord.record_failure(
            milestone_id=milestone_id, user_id=user_id, reason="距離が遠すぎる"
        )

        # Then
        assert record.milestone_id == milestone_id
        assert record.user_id == user_id
        assert record.status.achieved is False
        assert record.status.score == 0.0
        assert record.status.reason == "距離が遠すぎる"
        assert record.evidence.type == "manual"
        assert record.evidence.metadata["reason"] == "距離が遠すぎる"

    def test_達成記録にはIDが自動生成されること(self):
        """Given: 達成記録
        When: 作成
        Then: IDが自動生成される"""
        # Given
        milestone_id = uuid4()
        user_id = uuid4()
        verification_id = uuid4()

        # When
        record1 = AchievementRecord.record_achievement(
            milestone_id=milestone_id,
            user_id=user_id,
            verification_id=verification_id,
            score=0.95,
        )
        record2 = AchievementRecord.record_achievement(
            milestone_id=milestone_id,
            user_id=user_id,
            verification_id=verification_id,
            score=0.95,
        )

        # Then
        assert record1.id != record2.id

    def test_達成記録にはタイムスタンプが自動生成されること(self):
        """Given: 達成記録
        When: 作成
        Then: recorded_atが自動生成される"""
        # Given
        milestone_id = uuid4()
        user_id = uuid4()
        verification_id = uuid4()

        # When
        before = datetime.now(timezone.utc)
        record = AchievementRecord.record_achievement(
            milestone_id=milestone_id,
            user_id=user_id,
            verification_id=verification_id,
            score=0.95,
        )
        after = datetime.now(timezone.utc)

        # Then
        assert before <= record.recorded_at <= after

    def test_AchievementRecordは不変であること(self):
        """Given: AchievementRecord
        When: 属性を変更しようとする
        Then: エラーが発生する"""
        # Given
        record = AchievementRecord.record_achievement(
            milestone_id=uuid4(),
            user_id=uuid4(),
            verification_id=uuid4(),
            score=0.95,
        )

        # When/Then
        with pytest.raises(Exception):
            record.status = AchievementStatus(  # type: ignore
                achieved=False, score=0.0, reason=""
            )
