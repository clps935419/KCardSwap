"""Domain exceptions"""


class DomainError(Exception):
    """Base domain exception"""
    pass


class EntityNotFoundError(DomainError):
    """Entity not found error"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class BusinessRuleViolationError(DomainError):
    """Business rule violation error"""
    pass


class InvalidCredentialsError(DomainError):
    """Invalid credentials error"""
    pass


class UnauthorizedError(DomainError):
    """Unauthorized access error"""
    pass
