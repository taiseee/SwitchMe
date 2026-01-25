"""User domain model ↔ ORM model mappers"""

from domain.user.models import User, UserId, Email, OAuthProvider
from infrastructure.shared.models import UserModel


def user_to_orm(user: User) -> UserModel:
    """ドメインモデル → ORMモデル"""
    return UserModel(
        id=user.id.value,
        email=user.email.value,
        oauth_provider=user.oauth_provider.value,
        oauth_user_id=user.oauth_user_id,
        status=user.status.status,
        last_login_at=user.status.last_login_at,
    )


def orm_to_user(model: UserModel) -> User:
    """ORMモデル → ドメインモデル"""
    from domain.user.models import UserStatus

    return User(
        id=UserId(value=model.id),
        email=Email(value=model.email),
        oauth_provider=OAuthProvider(value=model.oauth_provider),
        oauth_user_id=model.oauth_user_id,
        status=UserStatus(status=model.status, last_login_at=model.last_login_at),
    )
