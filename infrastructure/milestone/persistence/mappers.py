"""Milestone domain model ↔ ORM model mappers"""

from domain.milestone.models import Milestone, MilestoneId, Title
from domain.milestone.value_objects import (
    DeadlineInfo,
    VerificationCriteria,
    PenaltyInfo,
)
from domain.user.models import UserId
from domain.shared.value_objects import Money
from infrastructure.shared.models import MilestoneModel
from datetime import date, time


def milestone_to_orm(milestone: Milestone) -> MilestoneModel:
    """ドメインモデル → ORMモデル"""
    return MilestoneModel(
        id=milestone.id.value,
        user_id=milestone.user_id.value,
        title=milestone.title.value,
        # DeadlineInfo展開
        deadline_date=milestone.deadline.deadline_date.isoformat(),
        deadline_time=milestone.deadline.deadline_time.isoformat(),
        timezone=milestone.deadline.timezone,
        # VerificationCriteria展開
        verification_type=milestone.verification_criteria.type,
        verification_conditions=milestone.verification_criteria.conditions,
        verification_threshold=milestone.verification_criteria.threshold,
        # PenaltyInfo展開
        penalty_amount=milestone.penalty.amount.amount,
        penalty_currency=milestone.penalty.amount.currency,
        penalty_description=milestone.penalty.description,
        status=milestone.status,
    )


def orm_to_milestone(model: MilestoneModel) -> Milestone:
    """ORMモデル → ドメインモデル"""
    return Milestone(
        id=MilestoneId(value=model.id),
        user_id=UserId(value=model.user_id),
        title=Title(value=model.title),
        deadline=DeadlineInfo(
            date=date.fromisoformat(model.deadline_date),
            time=time.fromisoformat(model.deadline_time),
            timezone=model.timezone,
        ),
        verification_criteria=VerificationCriteria(
            type=model.verification_type,
            conditions=model.verification_conditions,
            threshold=model.verification_threshold,
        ),
        penalty=PenaltyInfo(
            amount=Money(amount=model.penalty_amount, currency=model.penalty_currency),
            description=model.penalty_description,
        ),
        status=model.status,
    )
