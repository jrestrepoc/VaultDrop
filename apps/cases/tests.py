from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.cases.models import Caja, CajaItem, Item


class CajaItemProbabilidadTest(TestCase):
    def test_valida_total_de_probabilidades_en_caja(self):
        caja = Caja.objects.create(nombre='Caja Test', precio=Decimal('100.00'))
        item = Item.objects.create(nombre='Item Test')
        CajaItem.objects.create(caja=caja, item=item, probabilidad=Decimal('100.00'))

        CajaItem.validar_probabilidades(caja)


class CajaDetailAPITest(APITestCase):
    def test_caja_detail_success_200(self):
        caja = Caja.objects.create(nombre='Caja Gold', precio=Decimal('200.00'), activa=True)
        item = Item.objects.create(nombre='Cuchillo Dragón', rareza='LEGENDARIO', valor_estimado=Decimal('1500.00'))
        CajaItem.objects.create(caja=caja, item=item, probabilidad=Decimal('100.00'))

        url = reverse('cases:detail', kwargs={'caja_id': caja.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Caja Gold')
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['item']['nombre'], 'Cuchillo Dragón')

    def test_caja_detail_not_found_404(self):
        url = reverse('cases:detail', kwargs={'caja_id': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

