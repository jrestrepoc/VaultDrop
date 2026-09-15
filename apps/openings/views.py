from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.account import account_snapshot
from apps.core.operations import OperationService
from apps.openings.serializers import AperturaCajaSerializer, ItemInventarioSerializer
from apps.openings.services import AperturaCajaService
from apps.openings.inventory import InventoryService

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
        return Response(ItemInventarioSerializer(InventoryService().list_for_user(request.user), many=True).data)

class InventoryActionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    target_status = 'VENDIDO'

    def post(self, request, item_id):
        def action():
            item = InventoryService().change_status(request.user, item_id, self.target_status)
            return dict(ItemInventarioSerializer(item).data)
        data = OperationService().execute(request.user, request.headers.get('Idempotency-Key'),
                                          self.target_status, {'item_id': item_id}, action)
        return Response({'item': data, 'account': account_snapshot(request.user)})

class SendInventoryAPIView(InventoryActionAPIView):
    # The course project simulates delivery; no Steam integration is claimed.
    target_status = 'ENVIADO'
