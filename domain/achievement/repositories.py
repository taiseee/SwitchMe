"""達成記録リポジトリProtocol"""

from typing import Protocol
from uuid import UUID
from domain.achievement.models import AchievementRecord
from infrastructure.shared.result import Result
from domain.shared.exceptions import EntityNotFoundError


class AchievementRepository(Protocol):
    """達成記録リポジトリのインターフェース"""

    async def save(self, achievement: AchievementRecord) -> Result[None, Exception]:
        """達成記録を保存（INSERT or UPDATE）

        Args:
            achievement: 達成記録エンティティ

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        ...

    async def find_by_id(
        self, achievement_id: UUID
    ) -> Result[AchievementRecord, EntityNotFoundError]:
        """IDで達成記録を検索

        Args:
            achievement_id: 達成記録ID

        Returns:
            成功: Ok(AchievementRecord)
            失敗: Err(EntityNotFoundError)
        """
        ...

    async def find_by_milestone_id(
        self, milestone_id: UUID
    ) -> Result[list[AchievementRecord], Exception]:
        """マイルストーンIDで達成記録を検索

        Args:
            milestone_id: マイルストーンID

        Returns:
            成功: Ok(list[AchievementRecord])
            失敗: Err(Exception)
        """
        ...

    async def find_by_user_id(
        self, user_id: UUID
    ) -> Result[list[AchievementRecord], Exception]:
        """ユーザーIDで達成記録を検索

        Args:
            user_id: ユーザーID

        Returns:
            成功: Ok(list[AchievementRecord])
            失敗: Err(Exception)
        """
        ...

    async def delete(self, achievement_id: UUID) -> Result[None, Exception]:
        """達成記録を削除

        Args:
            achievement_id: 達成記録ID

        Returns:
            成功: Ok(None)
            失敗: Err(Exception)
        """
        ...
