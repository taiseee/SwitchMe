"""データベース接続管理のテスト"""

import os
from unittest.mock import patch
from infrastructure.shared.database import get_database_url, get_engine


class TestGetDatabaseUrl:
    """get_database_url()のテスト"""

    def test_環境変数からdatabase_urlが構築されること(self):
        """環境変数からDATABASE_URLが正しく構築されること"""
        with patch.dict(
            os.environ,
            {
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_USER": "testuser",
                "DB_PASSWORD": "testpass",
                "DB_NAME": "testdb",
            },
        ):
            url = get_database_url()
            assert url == "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"

    def test_デフォルト値でdatabase_urlが構築されること(self):
        """環境変数が設定されていない場合、デフォルト値でDATABASE_URLが構築されること"""
        with patch.dict(os.environ, {}, clear=True):
            url = get_database_url()
            assert "postgresql+asyncpg://" in url
            assert "switchme" in url  # デフォルトのDB名


class TestGetEngine:
    """get_engine()のテスト"""

    def test_エンジンが作成されること(self):
        """SQLAlchemyエンジンが作成されること"""
        with patch.dict(
            os.environ,
            {
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_USER": "testuser",
                "DB_PASSWORD": "testpass",
                "DB_NAME": "testdb",
            },
        ):
            engine = get_engine()
            assert engine is not None
            assert "postgresql+asyncpg" in str(engine.url)

    def test_同じエンジンインスタンスが返されること(self):
        """複数回呼び出しても同じエンジンインスタンスが返されること（シングルトン）"""
        with patch.dict(
            os.environ,
            {
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
                "DB_USER": "testuser",
                "DB_PASSWORD": "testpass",
                "DB_NAME": "testdb",
            },
        ):
            engine1 = get_engine()
            engine2 = get_engine()
            assert engine1 is engine2
