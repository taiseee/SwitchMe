"""Milestoneリポジトリ"""

from typing import Protocol
from domain.milestone.models import Milestone, MilestoneId
from domain.user.models import UserId
from infrastructure.shared.result import Result
from domain.shared.exceptions import EntityNotFoundError


class MilestoneRepository(Protocol):
    """Milestoneリポジトリのインターフェース

    ドメイン層で定義されるリポジトリインターフェース。
    実装はインフラ層で行う。
    """

    async def save(self, milestone: Milestone) -> Result[None, Exception]:
        """マイルストーンを保存する

        Args:
            milestone: 保存するマイルストーン

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        ...

    async def find_by_id(
        self, milestone_id: MilestoneId
    ) -> Result[Milestone, EntityNotFoundError]:
        """IDでマイルストーンを検索する

        Args:
            milestone_id: マイルストーンID

        Returns:
            成功時はOk(Milestone)、失敗時はErr(EntityNotFoundError)
        """
        ...

    async def find_by_user_id(
        self, user_id: UserId
    ) -> Result[list[Milestone], Exception]:
        """ユーザーIDでマイルストーンを検索する

        Args:
            user_id: ユーザーID

        Returns:
            成功時はOk(list[Milestone])、失敗時はErr(Exception)
        """
        ...

    async def delete(self, milestone_id: MilestoneId) -> Result[None, Exception]:
        """マイルストーンを削除する

        Args:
            milestone_id: マイルストーンID

        Returns:
            成功時はOk(None)、失敗時はErr(Exception)
        """
        ...

