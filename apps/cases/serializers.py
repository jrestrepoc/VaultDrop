from decimal import Decimal

from rest_framework import serializers

from apps.cases.models import Caja, CajaItem, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'nombre', 'rareza', 'valor_estimado']


class CajaItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CajaItem
        fields = ['item', 'probabilidad']


class CajaSerializer(serializers.ModelSerializer):
    items = CajaItemSerializer(source='caja_items', many=True)

    class Meta:
        model = Caja
        fields = ['id', 'nombre', 'descripcion', 'precio', 'activa', 'items']

    def validate(self, attrs):
        caja_items = attrs.get('caja_items', [])
        total = sum((item['probabilidad'] for item in caja_items), Decimal('0.00'))
        if caja_items and total != Decimal('100.00'):
            raise serializers.ValidationError('Las probabilidades de la caja deben sumar 100%')
        return attrs

