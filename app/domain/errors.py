class DomainError(Exception):
    code = "DOMAIN_ERROR"


class InvalidClientState(DomainError):
    code = "INVALID_STATE"

class DomainError(Exception):
    code = "DOMAIN_ERROR"


class OwnershipViolation(DomainError):
    code = "OWNERSHIP_VIOLATION"


class ResourceNotFound(DomainError):
    code = "NOT_FOUND"
