"""Achievement Repository統合テスト"""

import pytest
from uuid import uuid4
from domain.achievement.models import AchievementRecord
from domain.user.models import User, Email, OAuthProvider
from domain.milestone.models import Milestone, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.value_objects import Money
from infrastructure.achievement.persistence.repository import (
    PostgresAchievementRepository,
)
from infrastructure.user.persistence.repository import PostgresUserRepository
from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository
from infrastructure.shared.database import get_session_maker
from datetime import date, time


@pytest.mark.anyio
async def test_達成記録を保存して取得できること():
    """Given: 達成記録エンティティ
    When: 保存して取得
    Then: 同じ達成記録が取得できる"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="achievement_test1@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_achievement1",
    )
    milestone = Milestone.create(
        user_id=user.id,
        title=Title(value="朝のランニング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(7, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )

    session_maker = get_session_maker()
    async with session_maker() as session:
        user_repo = PostgresUserRepository(session)
        milestone_repo = PostgresMilestoneRepository(session)
        await user_repo.save(user)
        await milestone_repo.save(milestone)

    # Given: 達成記録
    verification_id = uuid4()
    achievement = AchievementRecord.record_achievement(
        milestone_id=milestone.id.value,
        user_id=user.id.value,
        verification_id=verification_id,
        score=0.95,
    )

    # When: 保存して取得
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        save_result = await repository.save(achievement)
        assert save_result.is_ok()

        result = await repository.find_by_id(achievement.id)

    # Then
    assert result.is_ok()
    found = result.unwrap()
    assert found.id == achievement.id
    assert found.milestone_id == milestone.id.value
    assert found.user_id == user.id.value
    assert found.status.achieved is True
    assert found.status.score == 0.95
    assert found.evidence.type == "verification"
    assert found.evidence.references == [verification_id]


@pytest.mark.anyio
async def test_失敗記録を保存して取得できること():
    """Given: 失敗記録
    When: 保存して取得
    Then: 同じ失敗記録が取得できる"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="achievement_test2@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_achievement2",
    )
    milestone = Milestone.create(
        user_id=user.id,
        title=Title(value="朝のランニング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(7, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )

    session_maker = get_session_maker()
    async with session_maker() as session:
        user_repo = PostgresUserRepository(session)
        milestone_repo = PostgresMilestoneRepository(session)
        await user_repo.save(user)
        await milestone_repo.save(milestone)

    # Given: 失敗記録
    achievement = AchievementRecord.record_failure(
        milestone_id=milestone.id.value,
        user_id=user.id.value,
        reason="距離が遠すぎる",
    )

    # When: 保存して取得
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        save_result = await repository.save(achievement)
        assert save_result.is_ok()

        result = await repository.find_by_id(achievement.id)

    # Then
    assert result.is_ok()
    found = result.unwrap()
    assert found.status.achieved is False
    assert found.status.score == 0.0
    assert found.status.reason == "距離が遠すぎる"
    assert found.evidence.type == "manual"


@pytest.mark.anyio
async def test_マイルストーンIDで達成記録を検索できること():
    """Given: 複数の達成記録
    When: マイルストーンIDで検索
    Then: 該当する達成記録リストが返される"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="achievement_test3@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_achievement3",
    )
    milestone1 = Milestone.create(
        user_id=user.id,
        title=Title(value="朝のランニング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(7, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )
    milestone2 = Milestone.create(
        user_id=user.id,
        title=Title(value="夕方のジョギング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(18, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6896, "lon": 139.7006},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )

    session_maker = get_session_maker()
    async with session_maker() as session:
        user_repo = PostgresUserRepository(session)
        milestone_repo = PostgresMilestoneRepository(session)
        await user_repo.save(user)
        await milestone_repo.save(milestone1)
        await milestone_repo.save(milestone2)

    # Given: milestone1に2つ、milestone2に1つの達成記録
    achievement1 = AchievementRecord.record_achievement(
        milestone_id=milestone1.id.value,
        user_id=user.id.value,
        verification_id=uuid4(),
        score=0.95,
    )
    achievement2 = AchievementRecord.record_failure(
        milestone_id=milestone1.id.value, user_id=user.id.value, reason="未達成"
    )
    achievement3 = AchievementRecord.record_achievement(
        milestone_id=milestone2.id.value,
        user_id=user.id.value,
        verification_id=uuid4(),
        score=0.80,
    )

    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        await repository.save(achievement1)
        await repository.save(achievement2)
        await repository.save(achievement3)

    # When: milestone1で検索
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        result = await repository.find_by_milestone_id(milestone1.id.value)

    # Then
    assert result.is_ok()
    found_list = result.unwrap()
    assert len(found_list) == 2
    assert all(a.milestone_id == milestone1.id.value for a in found_list)


@pytest.mark.anyio
async def test_ユーザーIDで達成記録を検索できること():
    """Given: 複数のユーザーの達成記録
    When: ユーザーIDで検索
    Then: 該当ユーザーの達成記録リストが返される"""
    # Given: 2人のユーザーとマイルストーンを事前作成
    user1 = User.create(
        email=Email(value="achievement_user1@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_achievement_user1",
    )
    user2 = User.create(
        email=Email(value="achievement_user2@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_achievement_user2",
    )
    milestone1 = Milestone.create(
        user_id=user1.id,
        title=Title(value="朝のランニング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(7, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )
    milestone2 = Milestone.create(
        user_id=user2.id,
        title=Title(value="夕方のジョギング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(18, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6896, "lon": 139.7006},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )

    session_maker = get_session_maker()
    async with session_maker() as session:
        user_repo = PostgresUserRepository(session)
        milestone_repo = PostgresMilestoneRepository(session)
        await user_repo.save(user1)
        await user_repo.save(user2)
        await milestone_repo.save(milestone1)
        await milestone_repo.save(milestone2)

    # Given: user1に2つ、user2に1つの達成記録
    achievement1 = AchievementRecord.record_achievement(
        milestone_id=milestone1.id.value,
        user_id=user1.id.value,
        verification_id=uuid4(),
        score=0.95,
    )
    achievement2 = AchievementRecord.record_failure(
        milestone_id=milestone1.id.value, user_id=user1.id.value, reason="未達成"
    )
    achievement3 = AchievementRecord.record_achievement(
        milestone_id=milestone2.id.value,
        user_id=user2.id.value,
        verification_id=uuid4(),
        score=0.80,
    )

    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        await repository.save(achievement1)
        await repository.save(achievement2)
        await repository.save(achievement3)

    # When: user1で検索
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        result = await repository.find_by_user_id(user1.id.value)

    # Then
    assert result.is_ok()
    found_list = result.unwrap()
    assert len(found_list) == 2
    assert all(a.user_id == user1.id.value for a in found_list)


@pytest.mark.anyio
async def test_存在しない達成記録のid検索はEntityNotFoundErrorを返すこと():
    """Given: 存在しないID
    When: IDで検索
    Then: EntityNotFoundError"""
    # Given
    non_existent_id = uuid4()

    # When
    session_maker = get_session_maker()
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        result = await repository.find_by_id(non_existent_id)

    # Then
    assert result.is_err()


@pytest.mark.anyio
async def test_達成記録を削除できること():
    """Given: 保存済み達成記録
    When: 削除
    Then: 達成記録が削除される"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="achievement_delete@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_achievement_delete",
    )
    milestone = Milestone.create(
        user_id=user.id,
        title=Title(value="朝のランニング"),
        deadline=DeadlineInfo(
            date=date(2026, 1, 27), time=time(7, 0), timezone="Asia/Tokyo"
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"), description="ペナルティ"
        ),
    )

    session_maker = get_session_maker()
    async with session_maker() as session:
        user_repo = PostgresUserRepository(session)
        milestone_repo = PostgresMilestoneRepository(session)
        await user_repo.save(user)
        await milestone_repo.save(milestone)

    achievement = AchievementRecord.record_achievement(
        milestone_id=milestone.id.value,
        user_id=user.id.value,
        verification_id=uuid4(),
        score=0.95,
    )

    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        await repository.save(achievement)

    # When: 削除
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        delete_result = await repository.delete(achievement.id)
        assert delete_result.is_ok()

    # Then: 取得できない
    async with session_maker() as session:
        repository = PostgresAchievementRepository(session)
        result = await repository.find_by_id(achievement.id)
        assert result.is_err()
