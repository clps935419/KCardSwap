"""Domain exceptions"""


class DomainException(Exception):
    """Base domain exception"""
    pass


class EntityNotFoundError(DomainException):
    """Entity not found error"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class BusinessRuleViolationError(DomainException):
    """Business rule violation error"""
    pass


class InvalidCredentialsError(DomainException):
    """Invalid credentials error"""
    pass


class UnauthorizedError(DomainException):
    """Unauthorized access error"""
    pass
