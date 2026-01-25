"""FastAPIアプリケーションのエントリーポイント"""

from fastapi import FastAPI
from apps.api.routers import auth_router, milestone_router

app = FastAPI(
    title="SwithMe API",
    description="Self-management support service with milestone tracking",
    version="0.1.0",
)


# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "ok"}


# ルーターの登録
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(milestone_router.router, prefix="/api/v1")
