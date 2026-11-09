from rest_framework import serializers

from apps.cases.serializers import CajaSerializer, ItemSerializer
from apps.openings.models import AperturaCaja, ItemInventario, Mejora


class ItemInventarioSerializer(serializers.ModelSerializer):
    caja_nombre = serializers.CharField(source='apertura.caja.nombre', read_only=True, default='')
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


class IdsField(serializers.ListField):
    child = serializers.IntegerField(min_value=1, max_value=2**63 - 1)


class AccionMasivaSerializer(serializers.Serializer):
    ids = IdsField(min_length=1, max_length=100)
    accion = serializers.ChoiceField(choices=['VENDIDO', 'ENVIADO'])


class MejorarSerializer(serializers.Serializer):
    ids = IdsField(min_length=1, max_length=6)
    objetivo = serializers.IntegerField(min_value=1, max_value=2**63 - 1)


class MejoraSerializer(serializers.ModelSerializer):
    objetivo = ItemSerializer()

    class Meta:
        model = Mejora
        fields = ['id', 'objetivo', 'valor_entregado', 'valor_objetivo', 'probabilidad', 'exito', 'created_at']


class AperturaHistorialSerializer(serializers.ModelSerializer):
    caja_nombre = serializers.CharField(source='caja.nombre', read_only=True)
    item = ItemSerializer()

    class Meta:
        model = AperturaCaja
        fields = ['id', 'caja_nombre', 'item', 'costo', 'created_at']


class RankingSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='user.username', read_only=True)
    item = ItemSerializer()

    class Meta:
        model = ItemInventario
        fields = ['id', 'usuario', 'item', 'created_at']
