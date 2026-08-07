class DomainError(Exception):
    pass


class EntityNotFoundError(DomainError):
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")


class DuplicateEntityError(DomainError):
    def __init__(self, entity_type: str, field: str, value: str):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(f"{entity_type} with {field} '{value}' already exists")


class ValidationError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    def __init__(self, permission: str):
        self.permission = permission
        super().__init__(f"Missing permission: {permission}")


class InvalidCredentialsError(AuthenticationError):
    pass


class TokenExpiredError(AuthenticationError):
    pass


class TokenInvalidError(AuthenticationError):
    pass


class PlanLimitExceededError(DomainError):
    def __init__(self, limit_type: str, current: int, maximum: int):
        self.limit_type = limit_type
        self.current = current
        self.maximum = maximum
        super().__init__(f"Plan limit exceeded: {limit_type} ({current}/{maximum})")


class MultiTenantViolationError(DomainError):
    pass


class InvalidStateTransitionError(DomainError):
    def __init__(self, entity_type: str, current: str, target: str):
        self.entity_type = entity_type
        self.current = current
        self.target = target
        super().__init__(
            f"Invalid {entity_type} transition: {current} -> {target}"
        )
