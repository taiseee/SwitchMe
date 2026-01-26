"""達成記録ユースケースのテスト"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from application.achievement.use_cases import (
    RecordAchievementInput,
    RecordAchievementUseCase,
    RecordFailureInput,
    RecordFailureUseCase,
    GetAchievementRecordsInput,
    GetAchievementRecordsUseCase,
)
from domain.achievement.models import AchievementRecord
from domain.achievement.repositories import AchievementRepository
from infrastructure.shared.result import Ok, Err


@pytest.fixture
def repository():
    """テスト用の達成記録リポジトリモック"""
    repo = Mock(spec=AchievementRepository)
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_milestone_id = AsyncMock()
    repo.find_by_user_id = AsyncMock()
    repo.delete = AsyncMock()
    return repo


class TestRecordAchievementUseCase:
    """RecordAchievementUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_達成記録が作成されること(self, repository):
        """Given: マイルストーンIDとユーザーID、検証ID
        When: RecordAchievementUseCaseを実行
        Then: 達成記録が作成され、リポジトリに保存される"""
        # Given
        repository.save.return_value = Ok(None)
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

        # リポジトリのsaveメソッドが正しく呼ばれたことを検証
        repository.save.assert_awaited_once()
        saved_record = repository.save.await_args.args[0]
        assert saved_record == record

    @pytest.mark.anyio
    async def test_保存に失敗した場合はErrを返すこと(self, repository):
        """Given: 保存に失敗するリポジトリ
        When: RecordAchievementUseCaseを実行
        Then: Errが返される"""
        # Given
        repository.save.return_value = Err(Exception("Database error"))
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
        repository.save.assert_awaited_once()


class TestRecordFailureUseCase:
    """RecordFailureUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_失敗記録が作成されること(self, repository):
        """Given: マイルストーンIDとユーザーID、失敗理由
        When: RecordFailureUseCaseを実行
        Then: 失敗記録が作成され、リポジトリに保存される"""
        # Given
        repository.save.return_value = Ok(None)
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

        # リポジトリのsaveメソッドが正しく呼ばれたことを検証
        repository.save.assert_awaited_once()
        saved_record = repository.save.await_args.args[0]
        assert saved_record == record

    @pytest.mark.anyio
    async def test_保存に失敗した場合はErrを返すこと(self, repository):
        """Given: 保存に失敗するリポジトリ
        When: RecordFailureUseCaseを実行
        Then: Errが返される"""
        # Given
        repository.save.return_value = Err(Exception("Database error"))
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
        repository.save.assert_awaited_once()


class TestGetAchievementRecordsUseCase:
    """GetAchievementRecordsUseCaseのテスト"""

    @pytest.mark.anyio
    async def test_ユーザーの達成記録が取得できること(self, repository):
        """Given: ユーザーの達成記録が存在する
        When: GetAchievementRecordsUseCaseを実行
        Then: 達成記録のリストが返される"""
        # Given
        user_id = uuid4()
        milestone_id1 = uuid4()
        milestone_id2 = uuid4()

        record1 = AchievementRecord.record_achievement(
            milestone_id=milestone_id1,
            user_id=user_id,
            verification_id=uuid4(),
            score=0.95,
        )
        record2 = AchievementRecord.record_failure(
            milestone_id=milestone_id2, user_id=user_id, reason="失敗"
        )

        repository.find_by_user_id.return_value = Ok([record1, record2])
        use_case = GetAchievementRecordsUseCase(repository)

        input_data = GetAchievementRecordsInput(user_id=str(user_id))

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        records = result.unwrap()
        assert len(records) == 2
        assert any(r.id == record1.id for r in records)
        assert any(r.id == record2.id for r in records)
        repository.find_by_user_id.assert_awaited_once_with(user_id)

    @pytest.mark.anyio
    async def test_達成記録がない場合は空リストが返されること(self, repository):
        """Given: ユーザーの達成記録が存在しない
        When: GetAchievementRecordsUseCaseを実行
        Then: 空のリストが返される"""
        # Given
        user_id = uuid4()
        repository.find_by_user_id.return_value = Ok([])
        use_case = GetAchievementRecordsUseCase(repository)

        input_data = GetAchievementRecordsInput(user_id=str(user_id))

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        records = result.unwrap()
        assert len(records) == 0
        repository.find_by_user_id.assert_awaited_once_with(user_id)

    @pytest.mark.anyio
    async def test_マイルストーンIDでフィルタできること(self, repository):
        """Given: 複数のマイルストーンの達成記録が存在する
        When: マイルストーンIDを指定してGetAchievementRecordsUseCaseを実行
        Then: 指定したマイルストーンの記録のみが返される"""
        # Given
        user_id = uuid4()
        milestone_id1 = uuid4()
        milestone_id2 = uuid4()

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

        # マイルストーンIDで検索した結果を返す
        repository.find_by_milestone_id.return_value = Ok([record1, record2])
        use_case = GetAchievementRecordsUseCase(repository)

        input_data = GetAchievementRecordsInput(
            user_id=str(user_id), milestone_id=str(milestone_id1)
        )

        # When
        result = await use_case.execute(input_data)

        # Then
        assert result.is_ok()
        records = result.unwrap()
        # ユーザーIDでフィルタされる
        assert len(records) == 2
        repository.find_by_milestone_id.assert_awaited_once_with(milestone_id1)
        # find_by_user_idは呼ばれないことを検証
        repository.find_by_user_id.assert_not_awaited()
