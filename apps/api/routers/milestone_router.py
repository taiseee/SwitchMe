"""Milestone APIルーター"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from domain.user.models import User
from domain.milestone.models import Milestone
from application.milestone.use_cases import (
    CreateMilestoneInput,
    CreateMilestoneUseCase,
    UpdateMilestoneInput,
    UpdateMilestoneUseCase,
    GetMilestonesUseCase,
    DeleteMilestoneUseCase,
)
from apps.api.dependencies import get_current_user, get_milestone_repository

router = APIRouter(prefix="/milestones", tags=["milestones"])


class CreateMilestoneRequest(BaseModel):
    """マイルストーン作成リクエスト"""

    title: str = Field(..., min_length=1, description="タイトル")
    deadline_date: str = Field(..., description="期限日（YYYY-MM-DD）")
    deadline_time: str = Field(..., description="期限時刻（HH:MM:SS）")
    timezone: str = Field(..., description="タイムゾーン")
    verification_type: str = Field(..., description="検証タイプ")
    verification_conditions: dict[str, Any] = Field(..., description="検証条件")
    verification_threshold: float = Field(..., description="検証閾値")
    penalty_amount: int = Field(..., ge=0, description="ペナルティ金額")
    penalty_currency: str = Field(..., description="通貨コード")
    penalty_description: str = Field(default="", description="ペナルティの説明")


class UpdateMilestoneRequest(BaseModel):
    """マイルストーン更新リクエスト"""

    title: str | None = Field(default=None, description="タイトル")
    deadline_date: str | None = Field(default=None, description="期限日（YYYY-MM-DD）")
    deadline_time: str | None = Field(default=None, description="期限時刻（HH:MM:SS）")
    timezone: str | None = Field(default=None, description="タイムゾーン")


class MilestoneResponse(BaseModel):
    """マイルストーンレスポンス"""

    id: str = Field(..., description="マイルストーンID")
    user_id: str = Field(..., description="ユーザーID")
    title: str = Field(..., description="タイトル")
    deadline: dict[str, Any] = Field(..., description="期限情報")
    verification_criteria: dict[str, Any] = Field(..., description="検証基準")
    penalty: dict[str, Any] = Field(..., description="ペナルティ情報")
    status: str = Field(..., description="ステータス")


def _milestone_to_response(milestone: Milestone) -> MilestoneResponse:
    """MilestoneをMilestoneResponseに変換する"""
    return MilestoneResponse(
        id=str(milestone.id.value),
        user_id=str(milestone.user_id.value),
        title=milestone.title.value,
        deadline={
            "date": milestone.deadline.deadline_date.isoformat(),
            "time": milestone.deadline.deadline_time.isoformat(),
            "timezone": milestone.deadline.timezone,
        },
        verification_criteria={
            "type": milestone.verification_criteria.type,
            "conditions": milestone.verification_criteria.conditions,
            "threshold": milestone.verification_criteria.threshold,
        },
        penalty={
            "amount": milestone.penalty.amount.amount,
            "currency": milestone.penalty.amount.currency,
            "description": milestone.penalty.description,
        },
        status=milestone.status,
    )


@router.post("", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(
    request: CreateMilestoneRequest,
    current_user: User = Depends(get_current_user),
    milestone_repository=Depends(get_milestone_repository),
):
    """マイルストーンを作成する

    Args:
        request: マイルストーン作成リクエスト
        current_user: 現在のユーザー（認証済み）

    Returns:
        作成されたマイルストーン
    """
    use_case = CreateMilestoneUseCase(milestone_repository)

    input_data = CreateMilestoneInput(
        user_id=str(current_user.id.value),
        title=request.title,
        deadline_date=request.deadline_date,
        deadline_time=request.deadline_time,
        timezone=request.timezone,
        verification_type=request.verification_type,
        verification_conditions=request.verification_conditions,
        verification_threshold=request.verification_threshold,
        penalty_amount=request.penalty_amount,
        penalty_currency=request.penalty_currency,
        penalty_description=request.penalty_description,
    )

    result = use_case.execute(input_data)

    if result.is_err():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.unwrap_err())
        )

    milestone = result.unwrap()
    return _milestone_to_response(milestone)


@router.get("", response_model=list[MilestoneResponse])
def get_milestones(
    current_user: User = Depends(get_current_user),
    milestone_repository=Depends(get_milestone_repository),
):
    """現在のユーザーのマイルストーン一覧を取得する

    Args:
        current_user: 現在のユーザー（認証済み）

    Returns:
        マイルストーン一覧
    """
    use_case = GetMilestonesUseCase(milestone_repository)

    result = use_case.execute(str(current_user.id.value))

    if result.is_err():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.unwrap_err())
        )

    milestones = result.unwrap()
    return [_milestone_to_response(m) for m in milestones]


@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: str,
    request: UpdateMilestoneRequest,
    current_user: User = Depends(get_current_user),
    milestone_repository=Depends(get_milestone_repository),
):
    """マイルストーンを更新する

    Args:
        milestone_id: マイルストーンID
        request: マイルストーン更新リクエスト
        current_user: 現在のユーザー（認証済み）

    Returns:
        更新されたマイルストーン
    """
    use_case = UpdateMilestoneUseCase(milestone_repository)

    input_data = UpdateMilestoneInput(
        milestone_id=milestone_id,
        user_id=str(current_user.id.value),
        title=request.title,
        deadline_date=request.deadline_date,
        deadline_time=request.deadline_time,
        timezone=request.timezone,
    )

    result = use_case.execute(input_data)

    if result.is_err():
        error = result.unwrap_err()
        if "not authorized" in str(error).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    milestone = result.unwrap()
    return _milestone_to_response(milestone)


@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: str,
    current_user: User = Depends(get_current_user),
    milestone_repository=Depends(get_milestone_repository),
):
    """マイルストーンを削除する

    Args:
        milestone_id: マイルストーンID
        current_user: 現在のユーザー（認証済み）

    Returns:
        成功メッセージ
    """
    use_case = DeleteMilestoneUseCase(milestone_repository)

    result = use_case.execute(milestone_id, str(current_user.id.value))

    if result.is_err():
        error = result.unwrap_err()
        if "not authorized" in str(error).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    return {"message": "Milestone deleted successfully"}
