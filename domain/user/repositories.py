"""Userリポジトリ"""

from typing import Protocol
from domain.user.models import User, UserId, Email, OAuthProvider
from infrastructure.shared.result import Result
from domain.shared.exceptions import EntityNotFoundError


class UserRepository(Protocol):
    """Userリポジトリのインターフェース

    ドメイン層で定義されるリポジトリインターフェース。
    実装はインフラ層で行う。
    """

    async def save(self, user: User) -> Result[None, Exception]:
        """ユーザーを保存する

        Args:
            user: 保存するユーザー

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        ...

    async def find_by_id(self, user_id: UserId) -> Result[User, EntityNotFoundError]:
        """IDでユーザーを検索する

        Args:
            user_id: ユーザーID

        Returns:
            成功時はOk(User)、失敗時はErr(EntityNotFoundError)
        """
        ...

    async def find_by_email(self, email: Email) -> Result[User, EntityNotFoundError]:
        """メールアドレスでユーザーを検索する

        Args:
            email: メールアドレス

        Returns:
            成功時はOk(User)、失敗時はErr(EntityNotFoundError)
        """
        ...

    async def find_by_oauth(
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

    async def delete(self, user_id: UserId) -> Result[None, Exception]:
        """ユーザーを削除する

        Args:
            user_id: ユーザーID

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        ...

