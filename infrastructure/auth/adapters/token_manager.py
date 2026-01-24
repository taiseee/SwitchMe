"""JWTトークンマネージャー"""

from typing import Protocol
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import jwt
from infrastructure.shared.result import Result, Ok, Err


class TokenPayload(BaseModel):
    """トークンペイロード"""

    user_id: str
    email: str
    exp: int


class TokenManager(Protocol):
    """トークンマネージャーのインターフェース"""

    def create_access_token(self, user_id: str, email: str) -> str:
        """アクセストークンを生成する

        Args:
            user_id: ユーザーID
            email: メールアドレス

        Returns:
            アクセストークン
        """
        ...

    def create_refresh_token(self, user_id: str) -> str:
        """リフレッシュトークンを生成する

        Args:
            user_id: ユーザーID

        Returns:
            リフレッシュトークン
        """
        ...

    def verify_token(self, token: str) -> Result[TokenPayload, str]:
        """トークンを検証する

        Args:
            token: JWTトークン

        Returns:
            成功時はOk(TokenPayload)、失敗時はErr(エラーメッセージ)
        """
        ...


class JWTTokenManager:
    """PyJWTベースのトークンマネージャー実装"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        """
        Args:
            secret_key: JWT署名用の秘密鍵
            algorithm: JWT署名アルゴリズム（デフォルト: HS256）
            access_token_expire_minutes: アクセストークンの有効期限（分）
            refresh_token_expire_days: リフレッシュトークンの有効期限（日）
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, user_id: str, email: str) -> str:
        """アクセストークンを生成する"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """リフレッシュトークンを生成する"""
        expire = datetime.now(timezone.utc) + timedelta(
            days=self.refresh_token_expire_days
        )
        payload = {
            "user_id": user_id,
            "email": "",  # リフレッシュトークンにはメールアドレスを含めない
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Result[TokenPayload, str]:
        """トークンを検証する"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return Ok(
                TokenPayload(
                    user_id=payload["user_id"],
                    email=payload["email"],
                    exp=payload["exp"],
                )
            )
        except jwt.ExpiredSignatureError:
            return Err("Token expired")
        except jwt.InvalidTokenError:
            return Err("Invalid token")
        except Exception as e:
            return Err(f"Token verification failed: {str(e)}")
