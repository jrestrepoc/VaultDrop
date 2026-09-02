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

