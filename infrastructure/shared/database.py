"""データベース接続管理"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)


_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    """データベース接続URLを構築する

    環境変数から接続情報を取得し、PostgreSQL接続URLを構築する。

    Returns:
        PostgreSQL接続URL（asyncpg形式）
    """
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "switchme")

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_engine() -> AsyncEngine:
    """SQLAlchemyエンジンを取得する（シングルトン）

    Returns:
        SQLAlchemy AsyncEngine
    """
    global _engine
    if _engine is None:
        database_url = get_database_url()
        _engine = create_async_engine(
            database_url,
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """セッションメーカーを取得する（シングルトン）

    Returns:
        SQLAlchemy async_sessionmaker
    """
    global _session_maker
    if _session_maker is None:
        engine = get_engine()
        _session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """セッションを取得する（依存性注入用）

    FastAPIのDepends()で使用するためのジェネレーター関数。

    Yields:
        SQLAlchemy AsyncSession
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session
