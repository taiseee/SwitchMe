"""Milestoneリポジトリ"""

from typing import Protocol
from domain.milestone.models import Milestone, MilestoneId
from domain.user.models import UserId
from infrastructure.shared.result import Result, Ok, Err
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


class InMemoryMilestoneRepository:
    """テスト用のインメモリMilestoneリポジトリ実装"""

    def __init__(self) -> None:
        self._milestones: dict[str, Milestone] = {}

    async def save(self, milestone: Milestone) -> Result[None, Exception]:
        """マイルストーンを保存する"""
        self._milestones[str(milestone.id.value)] = milestone
        return Ok(None)

    async def find_by_id(
        self, milestone_id: MilestoneId
    ) -> Result[Milestone, EntityNotFoundError]:
        """IDでマイルストーンを検索する"""
        milestone = self._milestones.get(str(milestone_id.value))
        if milestone is None:
            return Err(EntityNotFoundError("Milestone", str(milestone_id.value)))
        return Ok(milestone)

    async def find_by_user_id(
        self, user_id: UserId
    ) -> Result[list[Milestone], Exception]:
        """ユーザーIDでマイルストーンを検索する"""
        milestones = [
            m for m in self._milestones.values() if m.user_id.value == user_id.value
        ]
        return Ok(milestones)

    async def delete(self, milestone_id: MilestoneId) -> Result[None, Exception]:
        """マイルストーンを削除する"""
        milestone_id_str = str(milestone_id.value)
        if milestone_id_str not in self._milestones:
            return Err(EntityNotFoundError("Milestone", milestone_id_str))
        del self._milestones[milestone_id_str]
        return Ok(None)
