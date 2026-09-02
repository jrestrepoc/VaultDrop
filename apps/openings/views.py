from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.openings.exceptions import (
    CajaNoDisponibleError,
    CajaNoEncontradaError,
    CajaSinItemsError,
    ProbabilidadesInvalidasError,
    SaldoInsuficienteError,
)
from apps.openings.serializers import AperturaCajaSerializer
from apps.openings.services import AperturaCajaService


class AbrirCajaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    service_class = AperturaCajaService

    def post(self, request, caja_id):
        try:
            apertura, _ = self.service_class().abrir(request.user, caja_id)
        except CajaNoEncontradaError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except (CajaNoDisponibleError, SaldoInsuficienteError) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        except (CajaSinItemsError, ProbabilidadesInvalidasError, ValueError) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AperturaCajaSerializer(apertura)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

