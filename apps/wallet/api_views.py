from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.wallet.services import WalletService
from apps.wallet.serializers import BilleteraSerializer


class BilleteraAPIView(APIView):
    """Expositor DRF para consultar saldo e historial de transacciones.
    
    Requiere autenticación mediante Token o Sesión.
    Delega estrictamente en WalletService.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            billetera = WalletService().get_billetera(request.user)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = BilleteraSerializer(billetera)
        return Response(serializer.data, status=status.HTTP_200_OK)

