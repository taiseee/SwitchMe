"""Userリポジトリ"""

from typing import Protocol
from domain.user.models import User, UserId, Email, OAuthProvider
from infrastructure.shared.result import Result, Ok, Err
from domain.shared.exceptions import EntityNotFoundError


class UserRepository(Protocol):
    """Userリポジトリのインターフェース

    ドメイン層で定義されるリポジトリインターフェース。
    実装はインフラ層で行う。
    """

    def save(self, user: User) -> Result[None, Exception]:
        """ユーザーを保存する

        Args:
            user: 保存するユーザー

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        ...

    def find_by_id(self, user_id: UserId) -> Result[User, EntityNotFoundError]:
        """IDでユーザーを検索する

        Args:
            user_id: ユーザーID

        Returns:
            成功時はOk(User)、失敗時はErr(EntityNotFoundError)
        """
        ...

    def find_by_email(self, email: Email) -> Result[User, EntityNotFoundError]:
        """メールアドレスでユーザーを検索する

        Args:
            email: メールアドレス

        Returns:
            成功時はOk(User)、失敗時はErr(EntityNotFoundError)
        """
        ...

    def find_by_oauth(
        self, oauth_provider: OAuthProvider, oauth_user_id: str
    ) -> Result[User, EntityNotFoundError]:
        """OAuthプロバイダーとユーザーIDでユーザーを検索する

        Args:
            oauth_provider: OAuthプロバイダー
            oauth_user_id: OAuthプロバイダーのユーザーID

        Returns:
            成功時はOk(User)、失敗時はErr(EntityNotFoundError)
        """
        ...

    def delete(self, user_id: UserId) -> Result[None, Exception]:
        """ユーザーを削除する

        Args:
            user_id: ユーザーID

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        ...


class InMemoryUserRepository:
    """テスト用のインメモリUserリポジトリ実装"""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def save(self, user: User) -> Result[None, Exception]:
        """ユーザーを保存する"""
        self._users[str(user.id.value)] = user
        return Ok(None)

    def find_by_id(self, user_id: UserId) -> Result[User, EntityNotFoundError]:
        """IDでユーザーを検索する"""
        user = self._users.get(str(user_id.value))
        if user is None:
            return Err(EntityNotFoundError("User", str(user_id.value)))
        return Ok(user)

    def find_by_email(self, email: Email) -> Result[User, EntityNotFoundError]:
        """メールアドレスでユーザーを検索する"""
        for user in self._users.values():
            if user.email.value == email.value:
                return Ok(user)
        return Err(EntityNotFoundError("User", email.value))

    def find_by_oauth(
        self, oauth_provider: OAuthProvider, oauth_user_id: str
    ) -> Result[User, EntityNotFoundError]:
        """OAuthプロバイダーとユーザーIDでユーザーを検索する"""
        for user in self._users.values():
            if (
                user.oauth_provider == oauth_provider
                and user.oauth_user_id == oauth_user_id
            ):
                return Ok(user)
        return Err(
            EntityNotFoundError("User", f"{oauth_provider.value}:{oauth_user_id}")
        )

    def delete(self, user_id: UserId) -> Result[None, Exception]:
        """ユーザーを削除する"""
        user_id_str = str(user_id.value)
        if user_id_str not in self._users:
            return Err(EntityNotFoundError("User", user_id_str))
        del self._users[user_id_str]
        return Ok(None)
