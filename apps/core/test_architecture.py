from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO
from unittest.mock import Mock, patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.cases.models import Caja, CajaItem, Item
from apps.core.models import Operation
from apps.openings.models import AperturaCaja, ItemInventario
from apps.users.models import NotificacionEnvio
from apps.users.services import UserService
from apps.wallet.services import WalletService


class MutationContractTests(APITestCase):
    def setUp(self):
        self.user = UserService().register('architecture', 'architecture@example.test', 'strongpass')
        self.client.force_authenticate(self.user)
        self.case = Caja.objects.create(nombre='Test', precio=Decimal('25'))
        self.item = Item.objects.create(nombre='Test skin', valor_estimado=Decimal('10'), imagen_url='/static/test.png')
        CajaItem.objects.create(caja=self.case, item=self.item, probabilidad=Decimal('100'))

    def post(self, url, body=None, key=None):
        return self.client.post(url, body or {}, format='json', HTTP_IDEMPOTENCY_KEY=str(key or uuid4()))

    def open(self, key=None):
        response = self.post(f'/api/v1/cajas/{self.case.pk}/abrir/', key=key)
        self.assertEqual(response.status_code, 201, response.data)
        return response

    def test_simulated_send_notifies_after_commit(self):
        self.open()
        item = ItemInventario.objects.get()
        with patch('apps.openings.composition.NotificadorEnCola') as cola, self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.post(f'/api/v1/inventory/{item.pk}/send/').status_code, 200)
        cola.return_value.enviar_envio_simulado.assert_called_once_with(self.user, 'Test skin')

    def test_sale_does_not_send_a_shipping_notice(self):
        self.open()
        item = ItemInventario.objects.get()
        with patch('apps.openings.composition.NotificadorEnCola') as cola, self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.post(f'/api/v1/inventory/{item.pk}/sell/').status_code, 200)
        cola.return_value.enviar_envio_simulado.assert_not_called()

    def test_repeated_open_charges_once_and_returns_same_prize(self):
        key = uuid4()
        first, second = self.open(key), self.open(key)
        self.assertEqual(first.data['id'], second.data['id'])
        self.assertEqual(AperturaCaja.objects.count(), 1)
        self.assertEqual(ItemInventario.objects.count(), 1)
        self.assertEqual(second.data['account']['wallet']['saldo'], '975.00')

    def test_key_cannot_be_reused_with_a_different_amount(self):
        key = uuid4()
        self.assertEqual(self.post('/api/v1/wallet/deposit/', {'monto':'100.00'}, key).status_code, 200)
        self.assertEqual(self.post('/api/v1/wallet/deposit/', {'monto':'200.00'}, key).status_code, 409)
        self.assertEqual(WalletService().get_billetera(self.user).saldo, Decimal('1100'))

    def test_repeated_deposit_is_not_credited_twice(self):
        key = uuid4()
        for _ in range(2):
            response = self.post('/api/v1/wallet/deposit/', {'monto':'100.00'}, key)
            self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['account']['wallet']['saldo'], '1100.00')

    def test_sale_persists_and_cannot_be_repeated(self):
        item_id = self.open().data['inventario_item']['id']
        url = f'/api/v1/inventory/{item_id}/sell/'
        key = uuid4()
        self.assertEqual(self.post(url, key=key).status_code, 200)
        self.assertEqual(self.post(url, key=key).status_code, 200)
        self.assertEqual(self.post(url).status_code, 409)
        account = self.client.get('/api/v1/account/').data
        self.assertEqual(account['wallet']['saldo'], '985.00')
        self.assertEqual(account['inventory'][0]['estado'], 'VENDIDO')

    def test_send_is_simulated_persistent_and_excludes_sale(self):
        item_id = self.open().data['inventario_item']['id']
        self.assertEqual(self.post(f'/api/v1/inventory/{item_id}/send/').status_code, 200)
        self.assertEqual(self.post(f'/api/v1/inventory/{item_id}/sell/').status_code, 409)
        self.assertEqual(self.client.get('/api/v1/account/').data['inventory'][0]['estado'], 'ENVIADO')

    def test_cannot_sell_another_users_item(self):
        item_id = self.open().data['inventario_item']['id']
        other = UserService().register('other', 'other@example.test', 'strongpass')
        self.client.force_authenticate(other)
        self.assertEqual(self.post(f'/api/v1/inventory/{item_id}/sell/').status_code, 404)
        self.assertEqual(ItemInventario.objects.get(pk=item_id).estado, 'DISPONIBLE')
        self.assertEqual(self.client.get('/api/v1/account/').data['inventory'], [])

    def test_invalid_amounts_are_rejected_without_changes(self):
        for amount in ['-5', '0', 'NaN', 'Infinity', '1.234', '10001']:
            self.assertEqual(self.post('/api/v1/wallet/deposit/', {'monto':amount}).status_code, 400)
        self.assertEqual(WalletService().get_billetera(self.user).saldo, Decimal('1000'))

    def test_failed_open_rolls_back_charge_inventory_and_request_key(self):
        with patch('apps.openings.repositories.DjangoAperturaCajaRepository.create_inventario_item', side_effect=RuntimeError('write failed')):
            with self.assertRaises(RuntimeError):
                self.post(f'/api/v1/cajas/{self.case.pk}/abrir/')
        self.assertEqual(WalletService().get_billetera(self.user).saldo, Decimal('1000'))
        self.assertEqual(AperturaCaja.objects.count(), 0)
        self.assertEqual(Operation.objects.count(), 0)

    def test_insufficient_balance_produces_no_prize(self):
        self.case.precio = Decimal('1001')
        self.case.save()
        response = self.post(f'/api/v1/cajas/{self.case.pk}/abrir/')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'insufficient_balance')
        self.assertEqual(ItemInventario.objects.count(), 0)

    def test_profile_changes_survive_a_new_read(self):
        response = self.client.patch('/api/v1/auth/profile/', {'username':'updated','email':'updated@example.test','steam_username':'Steam demo'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updated')
        self.assertEqual(self.user.steam_username, 'Steam demo')

    def test_unauthenticated_mutation_is_rejected(self):
        self.client.force_authenticate(None)
        self.assertIn(self.post('/api/v1/wallet/deposit/', {'monto':'10'}).status_code, (401, 403))


class TransactionBoundaryTests(TestCase):
    def test_welcome_is_sent_only_after_commit(self):
        notifier = Mock()
        with self.captureOnCommitCallbacks(execute=True):
            UserService(notificador=notifier).register('commit', 'commit@example.test', 'strongpass')
            notifier.enviar_bienvenida.assert_not_called()
        notifier.enviar_bienvenida.assert_called_once()

    def test_rollback_does_not_send_welcome(self):
        notifier = Mock()
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError):
                with transaction.atomic():
                    UserService(notificador=notifier).register('rollback', 'rollback@example.test', 'strongpass')
                    raise RuntimeError('abort')
        notifier.enviar_bienvenida.assert_not_called()

    def test_seed_preserves_existing_prices_and_probabilities(self):
        case = Caja.objects.create(nombre='Fracture Case', precio=Decimal('123'))
        custom = Item.objects.create(nombre='Custom')
        CajaItem.objects.create(caja=case,item=custom,probabilidad=Decimal('100'))
        call_command('seed_catalog', verbosity=0)
        call_command('seed_catalog', verbosity=0)
        case.refresh_from_db()
        self.assertEqual(case.precio, Decimal('123'))
        self.assertEqual(list(case.caja_items.values_list('item_id',flat=True)),[custom.pk])


class FlujoCriticoTests(APITestCase):
    def test_registro_recarga_apertura_venta_y_envio_simulado(self):
        caso = Caja.objects.create(nombre='Prueba E2E', precio=Decimal('25'))
        premio = Item.objects.create(nombre='Premio E2E', valor_estimado=Decimal('10'))
        CajaItem.objects.create(caja=caso, item=premio, probabilidad=Decimal('100'))
        datos = {'username': 'e2e', 'email': 'e2e@example.test', 'password': 'vault-Test-4821'}
        self.assertEqual(self.client.post(reverse('users:api_register'), datos).status_code, 201)
        acceso = self.client.post(reverse('users:api_login'), {**datos, 'username': datos['email']})
        self.assertEqual(acceso.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {acceso.data['token']}")
        perfil = self.client.patch(reverse('users:profile'), {
            'username': datos['username'], 'email': datos['email'], 'steam_username': 'steam-e2e',
        })
        self.assertEqual(perfil.status_code, 200)
        self.assertEqual(self.client.get('/api/v1/cajas/').status_code, 200)
        self.assertEqual(self.client.post('/api/v1/wallet/deposit/', {'monto': '100.00'}).status_code, 200)

        for accion in ('sell', 'send'):
            apertura = self.client.post(f'/api/v1/cajas/{caso.pk}/abrir/')
            self.assertEqual(apertura.status_code, 201)
            item_id = apertura.data['inventario_item']['id']
            correo = StringIO()
            with patch.dict('os.environ', {'NOTIFICACION_MODE': 'SIMULADO'}), redirect_stdout(correo):
                with self.captureOnCommitCallbacks(execute=True):
                    respuesta = self.client.post(f'/api/v1/inventory/{item_id}/{accion}/')
            self.assertEqual(respuesta.status_code, 200)
        self.assertIn('steam-e2e', correo.getvalue())
        registro = NotificacionEnvio.objects.get()
        self.assertEqual(registro.usuario.username, datos['username'])
        self.assertEqual(registro.objetos, premio.nombre)
        self.assertEqual(respuesta.data['account']['wallet']['saldo'], '1060.00')
        self.assertEqual(respuesta.data['item']['estado'], 'ENVIADO')

        self.client.credentials()
        admin = get_user_model().objects.create_superuser('admin-e2e', 'admin@example.test', 'vault-Test-4821')
        self.client.force_login(admin)
        historial = self.client.get(reverse('admin:users_notificacionenvio_changelist'))
        self.assertContains(historial, premio.nombre)
