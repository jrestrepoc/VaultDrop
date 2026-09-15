from apps.core.domain import BusinessError, ConflictError, InsufficientBalanceError, NotFoundError

class CajaNoEncontradaError(NotFoundError):
    pass

class CajaNoDisponibleError(ConflictError):
    pass

class CajaSinItemsError(BusinessError):
    pass

class ProbabilidadesInvalidasError(BusinessError):
    pass

SaldoInsuficienteError = InsufficientBalanceError
