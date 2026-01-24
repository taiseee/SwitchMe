"""パスワードハッシュ化のテスト"""

from infrastructure.user.adapters.password_hasher import (
    BcryptPasswordHasher,
    InMemoryPasswordHasher,
)


class TestBcryptPasswordHasher:
    """BcryptPasswordHasherのテスト"""

    def test_パスワードをハッシュ化できること(self):
        """パスワードをハッシュ化できること"""
        hasher = BcryptPasswordHasher()
        password = "password123"
        hashed = hasher.hash(password)

        # ハッシュ化された文字列が返される
        assert hashed != password
        assert len(hashed) > 0
        # Bcryptのハッシュは$2b$で始まる
        assert hashed.startswith("$2b$")

    def test_パスワードを検証できること(self):
        """パスワードを検証できること"""
        hasher = BcryptPasswordHasher()
        password = "password123"
        hashed = hasher.hash(password)

        # 正しいパスワードは検証成功
        assert hasher.verify(password, hashed) is True

        # 間違ったパスワードは検証失敗
        assert hasher.verify("wrongpassword", hashed) is False


class TestInMemoryPasswordHasher:
    """InMemoryPasswordHasherのテスト"""

    def test_パスワードをハッシュ化できること(self):
        """パスワードをハッシュ化できること（テスト用の簡易実装）"""
        hasher = InMemoryPasswordHasher()
        password = "password123"
        hashed = hasher.hash(password)

        # プレフィックスが付いた文字列が返される
        assert hashed == f"hashed_{password}"

    def test_パスワードを検証できること(self):
        """パスワードを検証できること"""
        hasher = InMemoryPasswordHasher()
        password = "password123"
        hashed = hasher.hash(password)

        # 正しいパスワードは検証成功
        assert hasher.verify(password, hashed) is True

        # 間違ったパスワードは検証失敗
        assert hasher.verify("wrongpassword", hashed) is False
