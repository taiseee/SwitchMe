"""ユーザー関連のAPIルーター"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
import re
from application.user.use_cases import RegisterUserInput, RegisterUserUseCase
from apps.api.dependencies import get_user_repository, get_password_hasher


router = APIRouter()


class RegisterUserRequest(BaseModel):
    """ユーザー登録リクエスト"""

    email: str = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """メールアドレスの形式を検証"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v


class UserResponse(BaseModel):
    """ユーザーレスポンス"""

    id: str = Field(..., description="ユーザーID")
    email: str = Field(..., description="メールアドレス")
    status: dict = Field(..., description="ステータス")


@router.post(
    "/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    request: RegisterUserRequest,
    user_repository=Depends(get_user_repository),
    password_hasher=Depends(get_password_hasher),
):
    """ユーザー登録

    新しいユーザーを登録する。
    """
    # ユースケースの実行
    use_case = RegisterUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
    )

    input_data = RegisterUserInput(
        email=request.email,
        password=request.password,
    )

    result = use_case.execute(input_data)

    # エラーハンドリング
    if result.is_err():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(result._error),  # type: ignore
        )

    # 成功時のレスポンス
    user = result.unwrap()
    return UserResponse(
        id=str(user.id.value),
        email=user.email.value,
        status={
            "status": user.status.status,
            "last_login_at": user.status.last_login_at.isoformat()
            if user.status.last_login_at
            else None,
        },
    )
