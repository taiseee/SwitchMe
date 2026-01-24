"""Userドメインモデル"""

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
import re


class UserId(BaseModel):
    """ユーザーID（値オブジェクト）"""

    model_config = {"frozen": True}

    value: UUID = Field(...)


class Email(BaseModel):
    """メールアドレス（値オブジェクト）"""

    model_config = {"frozen": True}

    value: str = Field(...)

    @field_validator("value")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """メールアドレスの形式を検証"""
        # 簡易的なメールアドレスの正規表現
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v


class HashedPassword(BaseModel):
    """ハッシュ化されたパスワード（値オブジェクト）"""

    model_config = {"frozen": True}

    value: str = Field(...)


UserStatusType = Literal["active", "suspended", "deleted"]


class UserStatus(BaseModel):
    """ユーザーステータス（値オブジェクト）"""

    model_config = {"frozen": True}

    status: UserStatusType = Field(...)
    last_login_at: datetime | None = Field(default=None)


class User(BaseModel):
    """ユーザー（集約ルート）

    エンティティとしてIDによる同一性を持つ。
    不変（frozen）で、変更は新しいインスタンスを返すメソッドで行う。
    """

    model_config = {"frozen": True}

    id: UserId
    email: Email
    hashed_password: HashedPassword
    status: UserStatus

    @classmethod
    def create(cls, email: Email, hashed_password: HashedPassword) -> "User":
        """新しいユーザーを作成する

        Args:
            email: メールアドレス
            hashed_password: ハッシュ化されたパスワード

        Returns:
            作成されたユーザー
        """
        return cls(
            id=UserId(value=uuid4()),
            email=email,
            hashed_password=hashed_password,
            status=UserStatus(status="active", last_login_at=None),
        )

    def login(self) -> "User":
        """ログインして最終ログイン日時を更新する

        Returns:
            最終ログイン日時が更新された新しいUserインスタンス
        """
        return self.model_copy(
            update={
                "status": UserStatus(
                    status=self.status.status,
                    last_login_at=datetime.now(timezone.utc),
                )
            }
        )

    def delete_account(self) -> "User":
        """アカウントを削除する（論理削除）

        Returns:
            ステータスがdeletedに変更された新しいUserインスタンス
        """
        return self.model_copy(
            update={
                "status": UserStatus(
                    status="deleted",
                    last_login_at=self.status.last_login_at,
                )
            }
        )
