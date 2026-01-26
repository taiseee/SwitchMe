"""達成記録ユースケースのテスト"""

import pytest
from uuid import uuid4
from domain.achievement.models import AchievementRecord
from domain.shared.exceptions import EntityNotFoundError
from infrastructure.shared.result import Ok, Err
from application.achievement.use_cases import (
    RecordAchievementInput,
    RecordAchievementUseCase,
    RecordFailureInput,
    RecordFailureUseCase,
    GetAchievementRecordsInput,
    GetAchievementRecordsUseCase,
)


class InMemoryAchievementRepository:
    """テスト用インメモリ達成記録リポジトリ"""

    def __init__(self) -> None:
        self._achievements: dict[str, AchievementRecord] = {}

    async def save(self, achievement: AchievementRecord):
        """達成記録を保存"""
        self._achievements[str(achievement.id)] = achievement
        return Ok(None)

    async def find_by_id(self, achievement_id):
        """IDで達成記録を検索"""
        achievement = self._achievements.get(str(achievement_id))
        if achievement is None:
            return Err(EntityNotFoundError("Achievement not found"))
        return Ok(achievement)

    async def find_by_milestone_id(self, milestone_id):
        """マイルストーンIDで達成記録を検索"""
        records = [
            a for a in self._achievements.values() if a.milestone_id == milestone_id
        ]
        return Ok(records)

    async def find_by_user_id(self, user_id):
        """ユーザーIDで達成記録を検索"""
        records = [a for a in self._achievements.values() if a.user_id == user_id]
        return Ok(records)

    async def delete(self, achievement_id):
        """達成記録を削除"""
        if str(achievement_id) in self._achievements:
            del self._achievements[str(achievement_id)]
            return Ok(None)
        return Err(EntityNotFoundError("Achievement not found"))


class TestRecordAchievementUseCase:
    """RecordAchievementUseCaseのテスト"""

    @pytest.mark.asyncio
    async def test_達成記録が作成されること(self):
        """Given: マイルストーンIDとユーザーID、検証ID
        When: RecordAchievementUseCaseを実行
        Then: 達成記録が作成される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = RecordAchievementUseCase(repository)
        milestone_id = uuid4()
        user_id = uuid4()
        verification_id = uuid4()

        input_data = RecordAchievementInput(
            milestone_id=str(milestone_id),
            user_id=str(user_id),
            verification_id=str(verification_id),
            score=0.95,
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        record = result.unwrap()
        assert record.milestone_id == milestone_id
        assert record.user_id == user_id
        assert record.status.achieved is True
        assert record.status.score == 0.95
        assert record.evidence.type == "verification"
        assert record.evidence.references == [verification_id]

    @pytest.mark.asyncio
    async def test_達成記録が保存されること(self):
        """Given: 達成記録の入力
        When: RecordAchievementUseCaseを実行
        Then: リポジトリに保存される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = RecordAchievementUseCase(repository)
        milestone_id = uuid4()
        user_id = uuid4()
        verification_id = uuid4()

        input_data = RecordAchievementInput(
            milestone_id=str(milestone_id),
            user_id=str(user_id),
            verification_id=str(verification_id),
            score=0.95,
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        record = result.unwrap()

        # リポジトリから取得できることを確認
        find_result = await repository.find_by_id(record.id)
        assert find_result.is_ok()
        assert find_result.unwrap().id == record.id

    @pytest.mark.asyncio
    async def test_保存に失敗した場合はErrを返すこと(self):
        """Given: 保存に失敗するリポジトリ
        When: RecordAchievementUseCaseを実行
        Then: Errが返される"""

        # Given
        class FailingRepository:
            async def save(self, achievement):
                return Err(Exception("Database error"))

        repository = FailingRepository()
        use_case = RecordAchievementUseCase(repository)

        input_data = RecordAchievementInput(
            milestone_id=str(uuid4()),
            user_id=str(uuid4()),
            verification_id=str(uuid4()),
            score=0.95,
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_err()
        assert "Failed to save achievement" in str(result.unwrap_err())


class TestRecordFailureUseCase:
    """RecordFailureUseCaseのテスト"""

    @pytest.mark.asyncio
    async def test_失敗記録が作成されること(self):
        """Given: マイルストーンIDとユーザーID、失敗理由
        When: RecordFailureUseCaseを実行
        Then: 失敗記録が作成される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = RecordFailureUseCase(repository)
        milestone_id = uuid4()
        user_id = uuid4()

        input_data = RecordFailureInput(
            milestone_id=str(milestone_id),
            user_id=str(user_id),
            reason="距離が遠すぎる",
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        record = result.unwrap()
        assert record.milestone_id == milestone_id
        assert record.user_id == user_id
        assert record.status.achieved is False
        assert record.status.score == 0.0
        assert record.status.reason == "距離が遠すぎる"
        assert record.evidence.type == "manual"

    @pytest.mark.asyncio
    async def test_失敗記録が保存されること(self):
        """Given: 失敗記録の入力
        When: RecordFailureUseCaseを実行
        Then: リポジトリに保存される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = RecordFailureUseCase(repository)
        milestone_id = uuid4()
        user_id = uuid4()

        input_data = RecordFailureInput(
            milestone_id=str(milestone_id),
            user_id=str(user_id),
            reason="センサーデータなし",
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        record = result.unwrap()

        # リポジトリから取得できることを確認
        find_result = await repository.find_by_id(record.id)
        assert find_result.is_ok()
        assert find_result.unwrap().id == record.id

    @pytest.mark.asyncio
    async def test_保存に失敗した場合はErrを返すこと(self):
        """Given: 保存に失敗するリポジトリ
        When: RecordFailureUseCaseを実行
        Then: Errが返される"""

        # Given
        class FailingRepository:
            async def save(self, achievement):
                return Err(Exception("Database error"))

        repository = FailingRepository()
        use_case = RecordFailureUseCase(repository)

        input_data = RecordFailureInput(
            milestone_id=str(uuid4()),
            user_id=str(uuid4()),
            reason="テスト",
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_err()
        assert "Failed to save achievement" in str(result.unwrap_err())


class TestGetAchievementRecordsUseCase:
    """GetAchievementRecordsUseCaseのテスト"""

    @pytest.mark.asyncio
    async def test_ユーザーの達成記録が取得できること(self):
        """Given: ユーザーの達成記録が存在する
        When: GetAchievementRecordsUseCaseを実行
        Then: 達成記録のリストが返される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = GetAchievementRecordsUseCase(repository)
        user_id = uuid4()
        milestone_id1 = uuid4()
        milestone_id2 = uuid4()

        # 達成記録を作成
        record1 = AchievementRecord.record_achievement(
            milestone_id=milestone_id1,
            user_id=user_id,
            verification_id=uuid4(),
            score=0.95,
        )
        record2 = AchievementRecord.record_failure(
            milestone_id=milestone_id2, user_id=user_id, reason="失敗"
        )
        await repository.save(record1)
        await repository.save(record2)

        input_data = GetAchievementRecordsInput(user_id=str(user_id))

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        records = result.unwrap()
        assert len(records) == 2
        assert any(r.id == record1.id for r in records)
        assert any(r.id == record2.id for r in records)

    @pytest.mark.asyncio
    async def test_達成記録がない場合は空リストが返されること(self):
        """Given: ユーザーの達成記録が存在しない
        When: GetAchievementRecordsUseCaseを実行
        Then: 空のリストが返される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = GetAchievementRecordsUseCase(repository)
        user_id = uuid4()

        input_data = GetAchievementRecordsInput(user_id=str(user_id))

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        records = result.unwrap()
        assert len(records) == 0

    @pytest.mark.asyncio
    async def test_マイルストーンIDでフィルタできること(self):
        """Given: 複数のマイルストーンの達成記録が存在する
        When: マイルストーンIDを指定してGetAchievementRecordsUseCaseを実行
        Then: 指定したマイルストーンの記録のみが返される"""
        # Given
        repository = InMemoryAchievementRepository()
        use_case = GetAchievementRecordsUseCase(repository)
        user_id = uuid4()
        milestone_id1 = uuid4()
        milestone_id2 = uuid4()

        # 達成記録を作成
        record1 = AchievementRecord.record_achievement(
            milestone_id=milestone_id1,
            user_id=user_id,
            verification_id=uuid4(),
            score=0.95,
        )
        record2 = AchievementRecord.record_achievement(
            milestone_id=milestone_id2,
            user_id=user_id,
            verification_id=uuid4(),
            score=0.90,
        )
        await repository.save(record1)
        await repository.save(record2)

        input_data = GetAchievementRecordsInput(
            user_id=str(user_id), milestone_id=str(milestone_id1)
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        records = result.unwrap()
        assert len(records) == 1
        assert records[0].milestone_id == milestone_id1
