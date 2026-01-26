"""達成記録ユースケース"""

from uuid import UUID
from pydantic import BaseModel, Field
from domain.achievement.models import AchievementRecord
from domain.achievement.repositories import AchievementRepository
from infrastructure.shared.result import Result, Ok, Err


class RecordAchievementInput(BaseModel):
    """達成記録の入力モデル"""

    milestone_id: str = Field(..., description="マイルストーンID")
    user_id: str = Field(..., description="ユーザーID")
    verification_id: str = Field(..., description="検証ID")
    score: float = Field(..., ge=0, le=1, description="達成スコア（0〜1）")


class RecordFailureInput(BaseModel):
    """失敗記録の入力モデル"""

    milestone_id: str = Field(..., description="マイルストーンID")
    user_id: str = Field(..., description="ユーザーID")
    reason: str = Field(..., description="失敗理由")


class GetAchievementRecordsInput(BaseModel):
    """達成記録取得の入力モデル"""

    user_id: str = Field(..., description="ユーザーID")
    milestone_id: str | None = Field(
        default=None, description="マイルストーンID（オプション）"
    )


class RecordAchievementUseCase:
    """達成記録ユースケース

    マイルストーンの達成を記録する。
    """

    def __init__(self, achievement_repository: AchievementRepository) -> None:
        self._achievement_repository = achievement_repository

    async def execute(
        self, input_data: RecordAchievementInput
    ) -> Result[AchievementRecord, Exception]:
        """達成記録の作成と保存

        Args:
            input_data: 達成記録の入力データ

        Returns:
            成功: Ok(AchievementRecord)
            失敗: Err(Exception)
        """
        milestone_id = UUID(input_data.milestone_id)
        user_id = UUID(input_data.user_id)
        verification_id = UUID(input_data.verification_id)

        # 達成記録を作成
        record = AchievementRecord.record_achievement(
            milestone_id=milestone_id,
            user_id=user_id,
            verification_id=verification_id,
            score=input_data.score,
        )

        # 保存
        save_result = await self._achievement_repository.save(record)
        if save_result.is_err():
            return Err(Exception("Failed to save achievement"))

        return Ok(record)


class RecordFailureUseCase:
    """失敗記録ユースケース

    マイルストーンの未達成を記録する。
    """

    def __init__(self, achievement_repository: AchievementRepository) -> None:
        self._achievement_repository = achievement_repository

    async def execute(
        self, input_data: RecordFailureInput
    ) -> Result[AchievementRecord, Exception]:
        """失敗記録の作成と保存

        Args:
            input_data: 失敗記録の入力データ

        Returns:
            成功: Ok(AchievementRecord)
            失敗: Err(Exception)
        """
        milestone_id = UUID(input_data.milestone_id)
        user_id = UUID(input_data.user_id)

        # 失敗記録を作成
        record = AchievementRecord.record_failure(
            milestone_id=milestone_id, user_id=user_id, reason=input_data.reason
        )

        # 保存
        save_result = await self._achievement_repository.save(record)
        if save_result.is_err():
            return Err(Exception("Failed to save achievement"))

        return Ok(record)


class GetAchievementRecordsUseCase:
    """達成記録取得ユースケース

    ユーザーまたはマイルストーンの達成記録を取得する。
    """

    def __init__(self, achievement_repository: AchievementRepository) -> None:
        self._achievement_repository = achievement_repository

    async def execute(
        self, input_data: GetAchievementRecordsInput
    ) -> Result[list[AchievementRecord], Exception]:
        """達成記録の取得

        Args:
            input_data: 取得条件の入力データ

        Returns:
            成功: Ok(list[AchievementRecord])
            失敗: Err(Exception)
        """
        user_id = UUID(input_data.user_id)

        # マイルストーンIDが指定されている場合はそれで検索
        if input_data.milestone_id:
            milestone_id = UUID(input_data.milestone_id)
            result = await self._achievement_repository.find_by_milestone_id(
                milestone_id
            )
        else:
            # ユーザーIDで検索
            result = await self._achievement_repository.find_by_user_id(user_id)

        if result.is_err():
            return Err(result.unwrap_err())

        records = result.unwrap()

        # マイルストーンIDが指定されている場合は、さらにユーザーIDでフィルタ
        if input_data.milestone_id:
            records = [r for r in records if r.user_id == user_id]

        return Ok(records)
