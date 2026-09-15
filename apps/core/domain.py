"""Application errors independent of HTTP and persistence."""
class BusinessError(ValueError):
    code = 'invalid_operation'
    status_code = 400

class NotFoundError(BusinessError):
    code = 'not_found'
    status_code = 404

class ConflictError(BusinessError):
    code = 'conflict'
    status_code = 409

class InsufficientBalanceError(ConflictError):
    code = 'insufficient_balance'
