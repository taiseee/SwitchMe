"""Userユースケースのテスト"""

import pytest
from domain.user.models import Email
from domain.user.repositories import InMemoryUserRepository
from infrastructure.user.adapters.password_hasher import InMemoryPasswordHasher
from application.user.use_cases import RegisterUserInput, RegisterUserUseCase


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryUserRepository()


@pytest.fixture
def password_hasher():
    """テスト用のパスワードハッシュ化"""
    return InMemoryPasswordHasher()


@pytest.fixture
def use_case(repository, password_hasher):
    """RegisterUserUseCaseのインスタンス"""
    return RegisterUserUseCase(
        user_repository=repository,
        password_hasher=password_hasher,
    )


class TestRegisterUserUseCase:
    """RegisterUserUseCaseのテスト"""

    def test_ユーザー登録が成功すること(self, use_case, repository):
        """ユーザー登録が成功すること"""
        input_data = RegisterUserInput(
            email="test@example.com",
            password="password123",
        )

        # ユーザー登録
        result = use_case.execute(input_data)

        # 成功を確認
        assert result.is_ok()
        user = result.unwrap()
        assert user.email.value == "test@example.com"
        assert user.hashed_password.value == "hashed_password123"
        assert user.status.status == "active"

        # リポジトリに保存されていることを確認
        found_result = repository.find_by_email(Email(value="test@example.com"))
        assert found_result.is_ok()

    def test_同じメールアドレスでの登録は失敗すること(self, use_case):
        """同じメールアドレスでの登録は失敗すること"""
        input_data = RegisterUserInput(
            email="test@example.com",
            password="password123",
        )

        # 1回目の登録
        result1 = use_case.execute(input_data)
        assert result1.is_ok()

        # 2回目の登録（同じメールアドレス）
        result2 = use_case.execute(input_data)
        assert result2.is_err()
