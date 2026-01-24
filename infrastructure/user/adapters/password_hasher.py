"""パスワードハッシュ化アダプター"""

from typing import Protocol
import bcrypt


class PasswordHasher(Protocol):
    """パスワードハッシュ化のインターフェース"""

    def hash(self, password: str) -> str:
        """パスワードをハッシュ化する

        Args:
            password: 平文のパスワード

        Returns:
            ハッシュ化されたパスワード
        """
        ...

    def verify(self, password: str, hashed: str) -> bool:
        """パスワードを検証する

        Args:
            password: 平文のパスワード
            hashed: ハッシュ化されたパスワード

        Returns:
            パスワードが一致すればTrue、そうでなければFalse
        """
        ...


class BcryptPasswordHasher:
    """Bcryptを使用したパスワードハッシュ化実装"""

    def hash(self, password: str) -> str:
        """パスワードをハッシュ化する"""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        return hashed_bytes.decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        """パスワードを検証する"""
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)


class InMemoryPasswordHasher:
    """テスト用の簡易パスワードハッシュ化実装

    実際のハッシュ化は行わず、プレフィックスを付けるだけ。
    """

    def hash(self, password: str) -> str:
        """パスワードをハッシュ化する（簡易実装）"""
        return f"hashed_{password}"

    def verify(self, password: str, hashed: str) -> bool:
        """パスワードを検証する"""
        return hashed == f"hashed_{password}"
