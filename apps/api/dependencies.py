"""FastAPIの依存性注入"""

from domain.user.repositories import InMemoryUserRepository
from infrastructure.user.adapters.password_hasher import BcryptPasswordHasher

# シングルトンインスタンス（本番環境では適切なライフサイクル管理が必要）
_user_repository = InMemoryUserRepository()
_password_hasher = BcryptPasswordHasher()


def get_user_repository():
    """ユーザーリポジトリを取得"""
    return _user_repository


def get_password_hasher():
    """パスワードハッシュ化を取得"""
    return _password_hasher
