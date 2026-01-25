"""PostgreSQL Milestone Repository統合テスト"""

import pytest
from uuid import uuid4
from datetime import date, time

from domain.milestone.models import Milestone, MilestoneId, Title
from domain.milestone.value_objects import DeadlineInfo, VerificationCriteria, PenaltyInfo
from domain.user.models import User, UserId, Email, OAuthProvider
from domain.shared.value_objects import Money
from infrastructure.milestone.persistence.repository import PostgresMilestoneRepository
from infrastructure.user.persistence.repository import PostgresUserRepository


@pytest.mark.anyio
async def test_マイルストーンを保存して取得できること(db_session):
    """Given: 新しいマイルストーン
    When: 保存して取得
    Then: 保存したマイルストーンが取得できる"""
    # Given
    user_repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="test@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_123",
    )
    user_save_result = await user_repository.save(user)
    assert user_save_result.is_ok()
    
    repository = PostgresMilestoneRepository(db_session)
    user_id = user.id
    milestone = Milestone.create(
        user_id=user_id,
        title=Title(value="テストマイルストーン"),
        deadline=DeadlineInfo(
            date=date(2026, 12, 31),
            time=time(23, 59),
            timezone="Asia/Tokyo",
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="テストペナルティ",
        ),
    )

    # When
    save_result = await repository.save(milestone)
    assert save_result.is_ok()

    find_result = await repository.find_by_id(milestone.id)

    # Then
    assert find_result.is_ok()
    found = find_result.unwrap()
    assert found.id.value == milestone.id.value
    assert found.title.value == milestone.title.value
    assert found.user_id.value == user_id.value


@pytest.mark.anyio
async def test_ユーザーIDでマイルストーンを検索できること(db_session):
    """Given: 保存済みマイルストーン
    When: ユーザーIDで検索
    Then: マイルストーンのリストが取得できる"""
    # Given
    user_repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="test2@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_456",
    )
    user_save_result = await user_repository.save(user)
    assert user_save_result.is_ok()
    
    repository = PostgresMilestoneRepository(db_session)
    user_id = user.id
    milestone1 = Milestone.create(
        user_id=user_id,
        title=Title(value="マイルストーン1"),
        deadline=DeadlineInfo(
            date=date(2026, 12, 31),
            time=time(23, 59),
            timezone="Asia/Tokyo",
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="ペナルティ1",
        ),
    )
    milestone2 = Milestone.create(
        user_id=user_id,
        title=Title(value="マイルストーン2"),
        deadline=DeadlineInfo(
            date=date(2026, 12, 31),
            time=time(23, 59),
            timezone="Asia/Tokyo",
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=2000, currency="JPY"),
            description="ペナルティ2",
        ),
    )
    await repository.save(milestone1)
    await repository.save(milestone2)

    # When
    result = await repository.find_by_user_id(user_id)

    # Then
    assert result.is_ok()
    milestones = result.unwrap()
    assert len(milestones) == 2


@pytest.mark.anyio
async def test_存在しないマイルストーンのid検索はEntityNotFoundErrorを返すこと(db_session):
    """Given: 存在しないマイルストーンID
    When: ID検索
    Then: EntityNotFoundErrorを返す"""
    # Given
    repository = PostgresMilestoneRepository(db_session)
    non_existent_id = MilestoneId(value=uuid4())

    # When
    result = await repository.find_by_id(non_existent_id)

    # Then
    assert result.is_err()


@pytest.mark.anyio
async def test_マイルストーンが存在しないユーザーIDの検索は空リストを返すこと(db_session):
    """Given: マイルストーンが存在しないユーザーID
    When: ユーザーID検索
    Then: 空リストを返す"""
    # Given
    repository = PostgresMilestoneRepository(db_session)
    non_existent_user_id = UserId(value=uuid4())

    # When
    result = await repository.find_by_user_id(non_existent_user_id)

    # Then
    assert result.is_ok()
    milestones = result.unwrap()
    assert len(milestones) == 0


@pytest.mark.anyio
async def test_マイルストーンを削除できること(db_session):
    """Given: 保存済みマイルストーン
    When: 削除
    Then: 削除後は取得できない"""
    # Given
    user_repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="test3@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_789",
    )
    user_save_result = await user_repository.save(user)
    assert user_save_result.is_ok()
    
    repository = PostgresMilestoneRepository(db_session)
    user_id = user.id
    milestone = Milestone.create(
        user_id=user_id,
        title=Title(value="削除テスト"),
        deadline=DeadlineInfo(
            date=date(2026, 12, 31),
            time=time(23, 59),
            timezone="Asia/Tokyo",
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="削除ペナルティ",
        ),
    )
    await repository.save(milestone)

    # When
    delete_result = await repository.delete(milestone.id)
    assert delete_result.is_ok()

    # Then
    find_result = await repository.find_by_id(milestone.id)
    assert find_result.is_err()


@pytest.mark.anyio
async def test_マイルストーンを更新できること(db_session):
    """Given: 保存済みマイルストーン
    When: マイルストーン情報を更新
    Then: 更新後の情報で取得できる"""
    # Given
    user_repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="test4@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_101112",
    )
    user_save_result = await user_repository.save(user)
    assert user_save_result.is_ok()
    
    repository = PostgresMilestoneRepository(db_session)
    user_id = user.id
    milestone = Milestone.create(
        user_id=user_id,
        title=Title(value="更新前"),
        deadline=DeadlineInfo(
            date=date(2026, 12, 31),
            time=time(23, 59),
            timezone="Asia/Tokyo",
        ),
        verification_criteria=VerificationCriteria(
            type="location",
            conditions={"lat": 35.6812, "lon": 139.7671},
            threshold=100.0,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=1000, currency="JPY"),
            description="更新前ペナルティ",
        ),
    )
    await repository.save(milestone)

    # When: タイトルを更新
    updated_milestone = milestone.update(title=Title(value="更新後"))
    update_result = await repository.save(updated_milestone)
    assert update_result.is_ok()

    # Then
    find_result = await repository.find_by_id(milestone.id)
    assert find_result.is_ok()
    found = find_result.unwrap()
    assert found.title.value == "更新後"
