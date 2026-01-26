"""Verification Repository統合テスト"""

import pytest
from uuid import uuid4
from domain.verification.models import Verification, Location
from domain.user.models import User, Email, OAuthProvider
from domain.milestone.models import Milestone, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.shared.value_objects import Money
from infrastructure.verification.persistence.repository import (
    PostgresVerificationRepository,
)
from infrastructure.user.persistence.repository import PostgresUserRepository
from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository
from infrastructure.shared.database import get_session_maker
from datetime import date, time


@pytest.mark.anyio
async def test_検証を保存して取得できること():
    """Given: 検証エンティティ
    When: 保存して取得
    Then: 同じ検証が取得できる"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="test@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_123",
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

    # Given: 検証
    verification = Verification.create(
        milestone_id=milestone.id.value, user_id=user.id.value
    )

    # When: 保存して取得
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        save_result = await repository.save(verification)
        assert save_result.is_ok()

        result = await repository.find_by_id(verification.id)

    # Then
    assert result.is_ok()
    found = result.unwrap()
    assert found.id == verification.id
    assert found.milestone_id == milestone.id.value
    assert found.user_id == user.id.value
    assert found.status == "pending"


@pytest.mark.anyio
async def test_位置情報付き検証を保存して取得できること():
    """Given: 位置情報を含む検証
    When: 保存して取得
    Then: センサーデータが保存されている"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="test2@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_456",
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

    # Given: 位置情報を送信した検証
    verification = Verification.create(
        milestone_id=milestone.id.value, user_id=user.id.value
    )
    location = Location(latitude=35.6812, longitude=139.7671)
    verification = verification.submit_location(location, accuracy=5.0)

    # When: 保存して取得
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        save_result = await repository.save(verification)
        assert save_result.is_ok()

        result = await repository.find_by_id(verification.id)

    # Then
    assert result.is_ok()
    found = result.unwrap()
    assert found.status == "in_progress"
    assert len(found.sensor_data) == 1
    assert found.sensor_data[0].location.latitude == 35.6812
    assert found.sensor_data[0].location.longitude == 139.7671
    assert found.sensor_data[0].accuracy == 5.0


@pytest.mark.anyio
async def test_マイルストーンIDで検証を検索できること():
    """Given: 複数の検証
    When: マイルストーンIDで検索
    Then: 該当する検証リストが返される"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="test3@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_789",
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

    # Given: milestone1に2つ、milestone2に1つの検証
    verification1 = Verification.create(
        milestone_id=milestone1.id.value, user_id=user.id.value
    )
    verification2 = Verification.create(
        milestone_id=milestone1.id.value, user_id=user.id.value
    )
    verification3 = Verification.create(
        milestone_id=milestone2.id.value, user_id=user.id.value
    )

    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        await repository.save(verification1)
        await repository.save(verification2)
        await repository.save(verification3)

    # When: milestone1で検索
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        result = await repository.find_by_milestone_id(milestone1.id.value)

    # Then
    assert result.is_ok()
    found_list = result.unwrap()
    assert len(found_list) == 2
    assert all(v.milestone_id == milestone1.id.value for v in found_list)


@pytest.mark.anyio
async def test_ユーザーIDで検証を検索できること():
    """Given: 複数のユーザーの検証
    When: ユーザーIDで検索
    Then: 該当ユーザーの検証リストが返される"""
    # Given: 2人のユーザーとマイルストーンを事前作成
    user1 = User.create(
        email=Email(value="user1@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_user1",
    )
    user2 = User.create(
        email=Email(value="user2@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_user2",
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

    # Given: user1に2つ、user2に1つの検証
    verification1 = Verification.create(
        milestone_id=milestone1.id.value, user_id=user1.id.value
    )
    verification2 = Verification.create(
        milestone_id=milestone1.id.value, user_id=user1.id.value
    )
    verification3 = Verification.create(
        milestone_id=milestone2.id.value, user_id=user2.id.value
    )

    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        await repository.save(verification1)
        await repository.save(verification2)
        await repository.save(verification3)

    # When: user1で検索
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        result = await repository.find_by_user_id(user1.id.value)

    # Then
    assert result.is_ok()
    found_list = result.unwrap()
    assert len(found_list) == 2
    assert all(v.user_id == user1.id.value for v in found_list)


@pytest.mark.anyio
async def test_存在しない検証のid検索はEntityNotFoundErrorを返すこと():
    """Given: 存在しないID
    When: IDで検索
    Then: EntityNotFoundError"""
    # Given
    non_existent_id = uuid4()

    # When
    session_maker = get_session_maker()
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        result = await repository.find_by_id(non_existent_id)

    # Then
    assert result.is_err()


@pytest.mark.anyio
async def test_検証を削除できること():
    """Given: 保存済み検証
    When: 削除
    Then: 検証が削除される"""
    # Given: ユーザーとマイルストーンを事前作成
    user = User.create(
        email=Email(value="delete_test@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_delete",
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

    verification = Verification.create(
        milestone_id=milestone.id.value, user_id=user.id.value
    )

    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        await repository.save(verification)

    # When: 削除
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        delete_result = await repository.delete(verification.id)
        assert delete_result.is_ok()

    # Then: 取得できない
    async with session_maker() as session:
        repository = PostgresVerificationRepository(session)
        result = await repository.find_by_id(verification.id)
        assert result.is_err()
