from rest_framework import serializers

from apps.cases.serializers import CajaSerializer, ItemSerializer
from apps.openings.models import AperturaCaja, ItemInventario


class AbrirCajaSerializer(serializers.Serializer):
    caja_id = serializers.IntegerField(read_only=True)


class ItemInventarioSerializer(serializers.ModelSerializer):
    caja_nombre = serializers.CharField(source='apertura.caja.nombre', read_only=True)
    item = ItemSerializer()

    class Meta:
        model = ItemInventario
        fields = ['id', 'item', 'estado', 'created_at', 'caja_nombre']


class AperturaCajaSerializer(serializers.ModelSerializer):
    caja = CajaSerializer()
    item = ItemSerializer()
    inventario_item = ItemInventarioSerializer()

    class Meta:
        model = AperturaCaja
        fields = ['id', 'caja', 'item', 'costo', 'inventario_item', 'created_at']

