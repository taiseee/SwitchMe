"""PostgreSQL User Repository統合テスト"""

import pytest
from uuid import uuid4

from domain.user.models import User, UserId, Email, OAuthProvider
from infrastructure.user.persistence.repository import PostgresUserRepository


@pytest.mark.anyio
async def test_ユーザーを保存して取得できること(db_session):
    """Given: 新しいユーザー
    When: 保存して取得
    Then: 保存したユーザーが取得できる"""
    # Given
    repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="test@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_123",
    )

    # When
    save_result = await repository.save(user)
    assert save_result.is_ok()

    find_result = await repository.find_by_id(user.id)

    # Then
    assert find_result.is_ok()
    found_user = find_result.unwrap()
    assert found_user.id.value == user.id.value
    assert found_user.email.value == user.email.value
    assert found_user.oauth_provider == user.oauth_provider
    assert found_user.oauth_user_id == user.oauth_user_id


@pytest.mark.anyio
async def test_メールアドレスでユーザーを検索できること(db_session):
    """Given: 保存済みユーザー
    When: メールアドレスで検索
    Then: ユーザーが取得できる"""
    # Given
    repository = PostgresUserRepository(db_session)
    email = Email(value="search@example.com")
    user = User.create(
        email=email,
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_456",
    )
    await repository.save(user)

    # When
    result = await repository.find_by_email(email)

    # Then
    assert result.is_ok()
    found_user = result.unwrap()
    assert found_user.email.value == email.value


@pytest.mark.anyio
async def test_OAuthプロバイダーとユーザーIDでユーザーを検索できること(db_session):
    """Given: 保存済みユーザー
    When: OAuthプロバイダーとユーザーIDで検索
    Then: ユーザーが取得できる"""
    # Given
    repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="oauth@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_789",
    )
    await repository.save(user)

    # When
    oauth_provider = OAuthProvider()
    result = await repository.find_by_oauth(oauth_provider, "google_789")

    # Then
    assert result.is_ok()
    found_user = result.unwrap()
    assert found_user.oauth_provider.value == "google"
    assert found_user.oauth_user_id == "google_789"


@pytest.mark.anyio
async def test_存在しないユーザーのid検索はEntityNotFoundErrorを返すこと(db_session):
    """Given: 存在しないユーザーID
    When: ID検索
    Then: EntityNotFoundErrorを返す"""
    # Given
    repository = PostgresUserRepository(db_session)
    non_existent_id = UserId(value=uuid4())

    # When
    result = await repository.find_by_id(non_existent_id)

    # Then
    assert result.is_err()


@pytest.mark.anyio
async def test_存在しないユーザーのemail検索はEntityNotFoundErrorを返すこと(db_session):
    """Given: 存在しないメールアドレス
    When: email検索
    Then: EntityNotFoundErrorを返す"""
    # Given
    repository = PostgresUserRepository(db_session)
    non_existent_email = Email(value="nonexistent@example.com")

    # When
    result = await repository.find_by_email(non_existent_email)

    # Then
    assert result.is_err()


@pytest.mark.anyio
async def test_ユーザーを削除できること(db_session):
    """Given: 保存済みユーザー
    When: 削除
    Then: 削除後は取得できない"""
    # Given
    repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="delete@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_delete",
    )
    await repository.save(user)

    # When
    delete_result = await repository.delete(user.id)
    assert delete_result.is_ok()

    # Then
    find_result = await repository.find_by_id(user.id)
    assert find_result.is_err()


@pytest.mark.anyio
async def test_ユーザーを更新できること(db_session):
    """Given: 保存済みユーザー
    When: ユーザー情報を更新
    Then: 更新後の情報で取得できる"""
    # Given
    repository = PostgresUserRepository(db_session)
    user = User.create(
        email=Email(value="update@example.com"),
        oauth_provider=OAuthProvider(),
        oauth_user_id="google_update",
    )
    await repository.save(user)

    # When: ログインして最終ログイン日時を更新
    updated_user = user.login()
    update_result = await repository.save(updated_user)
    assert update_result.is_ok()

    # Then
    find_result = await repository.find_by_id(user.id)
    assert find_result.is_ok()
    found_user = find_result.unwrap()
    assert found_user.status.last_login_at is not None
