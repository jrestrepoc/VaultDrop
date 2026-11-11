from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.account import account_snapshot
from apps.core.operations import OperationService
from apps.openings.repositories import DjangoAperturaCajaRepository
from apps.openings.serializers import (
    AccionMasivaSerializer,
    AperturaCajaSerializer,
    AperturaHistorialSerializer,
    ItemInventarioSerializer,
    MejoraSerializer,
    MejorarSerializer,
    RankingSerializer,
)
from apps.openings.services import AperturaCajaService
from apps.openings.composition import crear_servicio_inventario
from apps.openings.upgrades import MejoraService

class AbrirCajaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    service_class = AperturaCajaService

    def post(self, request, caja_id):
        def action():
            apertura, _ = self.service_class().abrir(request.user, caja_id)
            return dict(AperturaCajaSerializer(apertura).data)
        data = OperationService().execute(request.user, request.headers.get('Idempotency-Key'),
                                          'open', {'caja_id': caja_id}, action)
        return Response({**data, 'account': account_snapshot(request.user)}, status=201)

class InventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ItemInventarioSerializer(crear_servicio_inventario().list_for_user(request.user), many=True).data)

class InventoryActionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    target_status = 'VENDIDO'

    def post(self, request, item_id):
        def action():
            item = crear_servicio_inventario().change_status(request.user, item_id, self.target_status)
            return dict(ItemInventarioSerializer(item).data)
        data = OperationService().execute(request.user, request.headers.get('Idempotency-Key'),
                                          self.target_status, {'item_id': item_id}, action)
        return Response({'item': data, 'account': account_snapshot(request.user)})

class SendInventoryAPIView(InventoryActionAPIView):
    # The course project simulates delivery; no Steam integration is claimed.
    target_status = 'ENVIADO'


class CajaGratisAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        def action():
            apertura, _ = AperturaCajaService().abrir_gratis(request.user)
            return dict(AperturaCajaSerializer(apertura).data)
        data = OperationService().execute(request.user, request.headers.get('Idempotency-Key'), 'free-open', {}, action)
        return Response({**data, 'account': account_snapshot(request.user)}, status=201)


class AccionMasivaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccionMasivaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids, accion = sorted(set(serializer.validated_data['ids'])), serializer.validated_data['accion']
        def action():
            return {'cantidad': len(crear_servicio_inventario().change_status_many(request.user, ids, accion))}
        data = OperationService().execute(request.user, request.headers.get('Idempotency-Key'),
                                          'bulk', {'ids': ids, 'accion': accion}, action)
        return Response({**data, 'account': account_snapshot(request.user)})


class MejorarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MejorarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids, objetivo = sorted(set(serializer.validated_data['ids'])), serializer.validated_data['objetivo']
        def action():
            return dict(MejoraSerializer(MejoraService().mejorar(request.user, ids, objetivo)).data)
        data = OperationService().execute(request.user, request.headers.get('Idempotency-Key'),
                                          'upgrade', {'ids': ids, 'objetivo': objetivo}, action)
        return Response({**data, 'account': account_snapshot(request.user)})


class HistorialAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        repository = DjangoAperturaCajaRepository()
        return Response({
            'aperturas': AperturaHistorialSerializer(repository.historial_aperturas(request.user, 50), many=True).data,
            'mejoras': MejoraSerializer(repository.historial_mejoras(request.user, 50), many=True).data,
        })


class RankingAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(RankingSerializer(DjangoAperturaCajaRepository().mejores_premios(10), many=True).data)
