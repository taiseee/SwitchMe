"""Userリポジトリのテスト"""

import pytest
from domain.user.models import User, UserId, Email, OAuthProvider
from domain.user.repositories import InMemoryUserRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryUserRepository()


@pytest.fixture
def sample_user():
    """テスト用のサンプルユーザー"""
    return User.create(
        email=Email(value="test@example.com"),
        oauth_provider=OAuthProvider(value="google"),
        oauth_user_id="google_user_123",
    )


class TestInMemoryUserRepository:
    """InMemoryUserRepositoryのテスト"""

    def test_ユーザーを保存して取得できること(self, repository, sample_user):
        """ユーザーを保存してIDで取得できること"""
        # 保存
        result = repository.save(sample_user)
        assert result.is_ok()

        # 取得
        found_result = repository.find_by_id(sample_user.id)
        assert found_result.is_ok()
        found_user = found_result.unwrap()
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    def test_メールアドレスでユーザーを検索できること(self, repository, sample_user):
        """メールアドレスでユーザーを検索できること"""
        # 保存
        repository.save(sample_user)

        # メールアドレスで検索
        found_result = repository.find_by_email(sample_user.email)
        assert found_result.is_ok()
        found_user = found_result.unwrap()
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    def test_OAuthプロバイダーとユーザーIDでユーザーを検索できること(
        self, repository, sample_user
    ):
        """OAuthプロバイダーとユーザーIDでユーザーを検索できること"""
        # 保存
        repository.save(sample_user)

        # OAuthで検索
        found_result = repository.find_by_oauth(
            oauth_provider=sample_user.oauth_provider,
            oauth_user_id=sample_user.oauth_user_id,
        )
        assert found_result.is_ok()
        found_user = found_result.unwrap()
        assert found_user.id == sample_user.id
        assert found_user.oauth_provider == sample_user.oauth_provider
        assert found_user.oauth_user_id == sample_user.oauth_user_id

    def test_存在しないユーザーのid検索はerrを返すこと(self, repository):
        """存在しないユーザーのID検索はErrを返すこと"""
        from uuid import uuid4

        non_existent_id = UserId(value=uuid4())
        result = repository.find_by_id(non_existent_id)
        assert result.is_err()

    def test_存在しないユーザーのemail検索はerrを返すこと(self, repository):
        """存在しないユーザーのメールアドレス検索はErrを返すこと"""
        non_existent_email = Email(value="nonexistent@example.com")
        result = repository.find_by_email(non_existent_email)
        assert result.is_err()

    def test_存在しないユーザーのOAuth検索はerrを返すこと(self, repository):
        """存在しないユーザーのOAuth検索はErrを返すこと"""
        result = repository.find_by_oauth(
            oauth_provider=OAuthProvider(value="google"),
            oauth_user_id="nonexistent_user_id",
        )
        assert result.is_err()

    def test_ユーザーを削除できること(self, repository, sample_user):
        """ユーザーを削除できること"""
        # 保存
        repository.save(sample_user)

        # 削除
        delete_result = repository.delete(sample_user.id)
        assert delete_result.is_ok()

        # 削除後は取得できない
        found_result = repository.find_by_id(sample_user.id)
        assert found_result.is_err()

    def test_存在しないユーザーの削除はerrを返すこと(self, repository):
        """存在しないユーザーの削除はErrを返すこと"""
        from uuid import uuid4

        non_existent_id = UserId(value=uuid4())
        result = repository.delete(non_existent_id)
        assert result.is_err()

    def test_ユーザーを更新できること(self, repository, sample_user):
        """同じIDのユーザーを保存すると更新されること"""
        # 最初に保存
        repository.save(sample_user)

        # ログインして更新
        updated_user = sample_user.login()
        repository.save(updated_user)

        # 取得して確認
        found_result = repository.find_by_id(sample_user.id)
        assert found_result.is_ok()
        found_user = found_result.unwrap()
        assert found_user.status.last_login_at is not None
