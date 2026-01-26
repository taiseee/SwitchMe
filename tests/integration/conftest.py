"""統合テスト用fixture"""

import os
import pytest
from sqlalchemy import text
from infrastructure.shared.database import reset_engine, get_engine


@pytest.fixture(scope="module", autouse=True)
async def setup_test_database():
    """テストデータベースのセットアップ（モジュールスコープ、自動実行）

    環境変数を設定し、アプリケーションコードがSupabaseに接続するようにする。
    """
    # Supabase接続用の環境変数を設定
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["DB_PORT"] = "54322"
    os.environ["DB_USER"] = "postgres"
    os.environ["DB_PASSWORD"] = "postgres"
    os.environ["DB_NAME"] = "postgres"

    # 既存のエンジンをリセット（環境変数変更を反映）
    await reset_engine()

    yield

    # テスト後：エンジンをクリーンアップ
    await reset_engine()


@pytest.fixture(autouse=True)
async def clear_database():
    """各テストの前後でデータベースをクリア（自動実行）"""
    engine = get_engine()

    # テスト前：データベースをクリア
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE milestones CASCADE"))
        await conn.execute(text("TRUNCATE TABLE users CASCADE"))

    yield

    # テスト後：データベースをクリア
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE milestones CASCADE"))
        await conn.execute(text("TRUNCATE TABLE users CASCADE"))
