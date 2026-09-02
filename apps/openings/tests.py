from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cases.models import Caja, CajaItem, Item
from apps.openings.exceptions import SaldoInsuficienteError
from apps.openings.models import AperturaCaja, ItemInventario
from apps.openings.services import AperturaCajaService
from apps.users.services import UserService


class FixedRandomizer:
    def __init__(self, value):
        self.value = value

    def uniform(self, start, end):
        return self.value


class AperturaCajaServiceTest(TestCase):
    def setUp(self):
        self.user = UserService().register(
            username='player',
            email='player@example.com',
            password='strongpass',
            initial_credit=Decimal('1000.00'),
        )
        self.caja = Caja.objects.create(nombre='Caja Bronze', precio=Decimal('250.00'), activa=True)
        self.item_comun = Item.objects.create(nombre='Sticker', rareza=Item.RAREZA_COMUN)
        self.item_raro = Item.objects.create(nombre='Skin rara', rareza=Item.RAREZA_RARO)
        CajaItem.objects.create(caja=self.caja, item=self.item_comun, probabilidad=Decimal('80.00'))
        CajaItem.objects.create(caja=self.caja, item=self.item_raro, probabilidad=Decimal('20.00'))

    def test_abrir_caja_debita_saldo_y_crea_inventario(self):
        service = AperturaCajaService(randomizer=FixedRandomizer(90))

        apertura, inventario_item = service.abrir(self.user, self.caja.id)

        self.user.billetera.refresh_from_db()
        self.assertEqual(self.user.billetera.saldo, Decimal('750.00'))
        self.assertEqual(apertura.item, self.item_raro)
        self.assertEqual(inventario_item.item, self.item_raro)
        self.assertTrue(AperturaCaja.objects.filter(user=self.user, caja=self.caja).exists())
        self.assertTrue(ItemInventario.objects.filter(user=self.user, item=self.item_raro).exists())

    def test_abrir_caja_sin_saldo_suficiente_lanza_error(self):
        self.caja.precio = Decimal('1500.00')
        self.caja.save()

        with self.assertRaises(SaldoInsuficienteError):
            AperturaCajaService(randomizer=FixedRandomizer(10)).abrir(self.user, self.caja.id)


class CajaApiTest(TestCase):
    def setUp(self):
        self.user = UserService().register(
            username='api-player',
            email='api-player@example.com',
            password='strongpass',
            initial_credit=Decimal('1000.00'),
        )
        self.caja = Caja.objects.create(nombre='Caja API', precio=Decimal('100.00'), activa=True)
        self.item = Item.objects.create(nombre='Item API', rareza=Item.RAREZA_EPICO)
        CajaItem.objects.create(caja=self.caja, item=self.item, probabilidad=Decimal('100.00'))

    def test_listar_cajas_activas(self):
        response = self.client.get(reverse('cases:list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['nombre'], 'Caja API')

    def test_abrir_caja_endpoint_crea_apertura(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('cases:open', kwargs={'caja_id': self.caja.id}))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['item']['nombre'], 'Item API')

    def test_abrir_caja_inexistente_responde_404(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('cases:open', kwargs={'caja_id': 9999}))

        self.assertEqual(response.status_code, 404)

    def test_abrir_caja_sin_autenticacion_responde_403(self):
        response = self.client.post(reverse('cases:open', kwargs={'caja_id': self.caja.id}))

        self.assertEqual(response.status_code, 403)
