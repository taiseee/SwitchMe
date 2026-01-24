"""ドメイン層の例外定義"""


class DomainException(Exception):
    """ドメイン層の基底例外"""

    pass


class DomainValidationError(DomainException):
    """ドメインバリデーションエラー"""

    pass


class EntityNotFoundError(DomainException):
    """エンティティが見つからないエラー"""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class UnauthorizedError(DomainException):
    """認証エラー"""

    pass
