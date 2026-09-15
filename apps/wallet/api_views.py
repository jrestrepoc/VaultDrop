from decimal import Decimal
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.account import account_snapshot
from apps.core.operations import OperationService
from apps.wallet.services import WalletService
from apps.wallet.serializers import BilleteraSerializer

class DepositInputSerializer(serializers.Serializer):
    monto = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0.01'), max_value=Decimal('10000.00'))

class BilleteraAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(BilleteraSerializer(WalletService().get_billetera(request.user)).data)

class DepositAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['monto']
        def action():
            wallet = WalletService().acreditar(request.user, amount)
            return {'wallet_id': wallet.pk, 'monto': str(amount)}
        result = OperationService().execute(request.user, request.headers.get('Idempotency-Key'),
                                            'deposit', {'monto': str(amount)}, action)
        return Response({**result, 'account': account_snapshot(request.user)})
