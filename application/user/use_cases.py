"""Userユースケース"""

from pydantic import BaseModel, Field
from domain.user.models import User, Email, HashedPassword
from domain.user.repositories import UserRepository
from infrastructure.user.adapters.password_hasher import PasswordHasher
from infrastructure.shared.result import Result, Ok, Err


class RegisterUserInput(BaseModel):
    """ユーザー登録の入力モデル"""

    email: str = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")


class RegisterUserUseCase:
    """ユーザー登録ユースケース

    新しいユーザーを登録する。
    メールアドレスの重複チェック、パスワードのハッシュ化、ユーザー作成と保存を行う。
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, input_data: RegisterUserInput) -> Result[User, Exception]:
        """ユーザー登録を実行する

        Args:
            input_data: 登録情報（メールアドレスとパスワード）

        Returns:
            成功時はOk(User)、失敗時はErr(Exception)
        """
        # メールアドレスの重複チェック
        email = Email(value=input_data.email)
        existing_user_result = self._user_repository.find_by_email(email)
        if existing_user_result.is_ok():
            return Err(ValueError(f"Email {input_data.email} is already registered"))

        # パスワードのハッシュ化
        hashed_password_str = self._password_hasher.hash(input_data.password)
        hashed_password = HashedPassword(value=hashed_password_str)

        # ユーザー作成
        user = User.create(email=email, hashed_password=hashed_password)

        # ユーザー保存
        save_result = self._user_repository.save(user)
        if save_result.is_err():
            return Err(Exception("Failed to save user"))

        return Ok(user)
