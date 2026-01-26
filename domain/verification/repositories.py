"""検証リポジトリProtocol"""

from typing import Protocol
from uuid import UUID
from domain.verification.models import Verification
from infrastructure.shared.result import Result
from domain.shared.exceptions import EntityNotFoundError


class VerificationRepository(Protocol):
    """検証リポジトリのインターフェース"""

    async def save(self, verification: Verification) -> Result[None, Exception]:
        """検証を保存（INSERT or UPDATE）

        Args:
            verification: 検証エンティティ

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        ...

    async def find_by_id(
        self, verification_id: UUID
    ) -> Result[Verification, EntityNotFoundError]:
        """IDで検証を検索

        Args:
            verification_id: 検証ID

        Returns:
            成功: Ok(Verification)
            失敗: Err(EntityNotFoundError)
        """
        ...

    async def find_by_milestone_id(
        self, milestone_id: UUID
    ) -> Result[list[Verification], Exception]:
        """マイルストーンIDで検証を検索

        Args:
            milestone_id: マイルストーンID

        Returns:
            成功: Ok(list[Verification])
            失敗: Err(Exception)
        """
        ...

    async def find_by_user_id(
        self, user_id: UUID
    ) -> Result[list[Verification], Exception]:
        """ユーザーIDで検証を検索

        Args:
            user_id: ユーザーID

        Returns:
            成功: Ok(list[Verification])
            失敗: Err(Exception)
        """
        ...

    async def delete(self, verification_id: UUID) -> Result[None, Exception]:
        """検証を削除

        Args:
            verification_id: 検証ID

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        ...
