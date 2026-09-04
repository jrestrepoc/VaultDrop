from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cases.repositories import DjangoCajaRepository
from apps.cases.serializers import CajaSerializer


class CajaListAPIView(APIView):
    permission_classes = [AllowAny]
    caja_repository_class = DjangoCajaRepository

    def get(self, request):
        cajas = self.caja_repository_class().list_activas()
        serializer = CajaSerializer(cajas, many=True)
        return Response(serializer.data)


class CajaDetailAPIView(APIView):
    """Expositor DRF para consultar el detalle de una caja individual y sus ítems."""
    permission_classes = [AllowAny]
    caja_repository_class = DjangoCajaRepository

    def get(self, request, caja_id):
        caja = self.caja_repository_class().get_by_id(caja_id)
        if not caja:
            return Response({'detail': 'Caja no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CajaSerializer(caja)
        return Response(serializer.data, status=status.HTTP_200_OK)


