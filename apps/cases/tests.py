from decimal import Decimal

from django.test import TestCase

from apps.cases.models import Caja, CajaItem, Item


class CajaItemProbabilidadTest(TestCase):
    def test_valida_total_de_probabilidades_en_caja(self):
        caja = Caja.objects.create(nombre='Caja Test', precio=Decimal('100.00'))
        item = Item.objects.create(nombre='Item Test')
        CajaItem.objects.create(caja=caja, item=item, probabilidad=Decimal('100.00'))

        CajaItem.validar_probabilidades(caja)
