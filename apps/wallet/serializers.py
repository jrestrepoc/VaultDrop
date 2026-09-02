from rest_framework import serializers
from apps.wallet.models import Billetera, Transaccion


class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = ('id', 'tipo', 'monto', 'saldo_anterior', 'saldo_posterior', 'created_at')
        read_only_fields = fields


class BilleteraSerializer(serializers.ModelSerializer):
    transacciones = TransaccionSerializer(many=True, read_only=True)

    class Meta:
        model = Billetera
        fields = ('id', 'saldo', 'transacciones')
        read_only_fields = fields

