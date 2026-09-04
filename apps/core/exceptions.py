from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from apps.openings.exceptions import (
    CajaNoEncontradaError,
    CajaNoDisponibleError,
    CajaSinItemsError,
    ProbabilidadesInvalidasError,
    SaldoInsuficienteError,
)


def custom_exception_handler(exc, context):
    """Manejador global de excepciones para Django Rest Framework.
    
    Captura excepciones de dominio y negocio no manejadas nativamente por DRF
    y las traduce a códigos de estado HTTP empresariales y respuestas JSON uniformes:
      - 404 Not Found: recursos inexistentes.
      - 409 Conflict: recursos en estado no disponible o duplicados.
      - 400 Bad Request: reglas de validación de negocio o saldo insuficiente.
    """
    # 1. Intentar resolver con el manejador por defecto de DRF
    response = exception_handler(exc, context)
    if response is not None:
        return response

    # 2. Manejo de excepciones específicas de la capa de dominio
    if isinstance(exc, CajaNoEncontradaError):
        return Response(
            {'detail': str(exc), 'code': 'not_found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if isinstance(exc, CajaNoDisponibleError):
        return Response(
            {'detail': str(exc), 'code': 'conflict'},
            status=status.HTTP_409_CONFLICT
        )

    if isinstance(exc, (SaldoInsuficienteError, CajaSinItemsError, ProbabilidadesInvalidasError)):
        return Response(
            {'detail': str(exc), 'code': 'bad_request'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Manejo de ValueError estándar de servicios (ej. validaciones de UserService y WalletService)
    if isinstance(exc, ValueError):
        msg = str(exc)
        if 'ya está en uso' in msg or 'ya está registrado' in msg or 'ya están registrados' in msg:
            return Response(
                {'detail': msg, 'code': 'conflict'},
                status=status.HTTP_409_CONFLICT
            )
        if 'no posee una billetera' in msg:
            return Response(
                {'detail': msg, 'code': 'not_found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {'detail': msg, 'code': 'bad_request'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Si es otra excepción no controlada, dejar que Django la maneje (500)
    return None

