"""テスト用の共通fixture"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from apps.api.main import app
from infrastructure.shared.database import get_database_url
from infrastructure.shared.database import get_session
from infrastructure.shared.models import Base

DEFAULT_TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres"
)


def _build_candidate_database_urls() -> list[str]:
    """接続を試行するDB URL候補を構築する"""
    candidates: list[str] = []

    test_database_url = os.getenv("TEST_DATABASE_URL")
    if test_database_url:
        candidates.append(test_database_url)

    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url not in candidates:
        candidates.append(database_url)

    base_url = get_database_url()
    test_base_url = base_url.replace("/switchme", "/switchme_test")
    for url in (test_base_url, base_url, DEFAULT_TEST_DATABASE_URL):
        if url not in candidates:
            candidates.append(url)

    return candidates


async def _create_engine_with_fallback() -> AsyncEngine:
    """接続可能なDB URLを順に試し、エンジンを作成する"""
    last_error: Exception | None = None

    for database_url in _build_candidate_database_urls():
        candidate_engine = create_async_engine(database_url, echo=False)
        try:
            async with candidate_engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return candidate_engine
        except Exception as exc:  # pragma: no cover - 接続確認の防御コード
            last_error = exc
            await candidate_engine.dispose()

    assert last_error is not None
    raise last_error


async def _reset_database(session: AsyncSession) -> None:
    """テスト開始前にDBを空にする（トランザクション内）"""
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.flush()


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """テスト用エンジン"""
    test_engine = await _create_engine_with_fallback()

    # テーブルが存在しない環境でも動作するように作成しておく
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    await test_engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """各テストで独立したセッションを提供する"""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        # リポジトリ側はcommitせずflushする
        session.info["skip_commit"] = True

        try:
            await _reset_database(session)
            yield session
        finally:
            await session.close()
            if transaction.is_active:
                await transaction.rollback()


@pytest.fixture
async def app_with_db(db_session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    """DBセッションをFastAPI依存性に注入したアプリ"""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """anyioのバックエンドを固定する"""
    return "asyncio"
