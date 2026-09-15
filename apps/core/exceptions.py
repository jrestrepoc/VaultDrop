from rest_framework.response import Response
from rest_framework.views import exception_handler
from apps.core.domain import BusinessError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response
    if isinstance(exc, BusinessError):
        return Response({'detail': str(exc), 'code': exc.code}, status=exc.status_code)
    if isinstance(exc, ValueError):
        return Response({'detail': str(exc), 'code': 'bad_request'}, status=400)
    return None
