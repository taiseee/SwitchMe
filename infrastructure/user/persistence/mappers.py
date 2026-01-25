"""User domain model ↔ ORM model mappers"""

from domain.user.models import User, UserId, Email
from infrastructure.shared.models import UserModel


def user_to_orm(user: User) -> UserModel:
    """ドメインモデル → ORMモデル"""
    return UserModel(
        id=user.id.value,
        email=user.email.value,
        oauth_provider=user.oauth_provider,
        oauth_user_id=user.oauth_user_id,
        status=user.status,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def orm_to_user(model: UserModel) -> User:
    """ORMモデル → ドメインモデル"""
    return User(
        id=UserId(value=model.id),
        email=Email(value=model.email),
        oauth_provider=model.oauth_provider,
        oauth_user_id=model.oauth_user_id,
        status=model.status,
        last_login_at=model.last_login_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
