from rest_framework import serializers

from apps.cases.models import Caja, CajaItem, Item


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = ['id', 'nombre', 'imagen_url', 'rareza', 'valor_estimado']


class CajaItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CajaItem
        fields = ['item', 'probabilidad']


class CajaSerializer(serializers.ModelSerializer):

    items = CajaItemSerializer(source='caja_items', many=True)

    class Meta:
        model = Caja
        fields = ['id', 'nombre', 'imagen_url', 'descripcion', 'precio', 'activa', 'items']

