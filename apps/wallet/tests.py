from io import BytesIO
from unittest import mock
from urllib.error import URLError

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from decimal import Decimal

from apps.core.domain import ExternalServiceError
from apps.users.services import UserService
from apps.wallet.infra.exchange_rates import ExchangeRateApiAdapter, IProveedorTasaCambio
from apps.wallet.services import CotizacionService

URLOPEN = 'apps.wallet.infra.exchange_rates.urlopen'
RESPUESTA_OK = b'{"result":"success","rates":{"COP":3243.549}}'


class ExchangeRateApiAdapterTest(SimpleTestCase):
    def test_translates_the_api_response(self):
        with mock.patch(URLOPEN, return_value=BytesIO(RESPUESTA_OK)):
            self.assertEqual(ExchangeRateApiAdapter().obtener_tasa('COP'), Decimal('3243.549'))

    def test_any_provider_failure_becomes_one_application_error(self):
        fallos = [
            {'side_effect': URLError('sin red')},
            {'side_effect': TimeoutError()},
            {'return_value': BytesIO(b'<html>no es json</html>')},
            {'return_value': BytesIO(b'{"result":"error"}')},
            {'return_value': BytesIO(b'{"rates":{"COP":0}}')},
            {'return_value': BytesIO(b'{"rates":{"COP":"abc"}}')},
        ]
        for fallo in fallos:
            with self.subTest(fallo), mock.patch(URLOPEN, **fallo), self.assertLogs(level='WARNING'):
                with self.assertRaises(ExternalServiceError):
                    ExchangeRateApiAdapter().obtener_tasa('COP')


class CotizacionServiceTest(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.proveedor = mock.create_autospec(IProveedorTasaCambio, instance=True)

    def test_depends_only_on_the_contract_and_caches_the_rate(self):
        self.proveedor.obtener_tasa.return_value = Decimal('4000')
        servicio = CotizacionService(self.proveedor)
        self.assertEqual(servicio.tasa('COP'), Decimal('4000'))
        self.assertEqual(servicio.tasa('COP'), Decimal('4000'))
        self.proveedor.obtener_tasa.assert_called_once_with('COP')

    def test_failure_is_remembered_so_pages_do_not_wait_again(self):
        self.proveedor.obtener_tasa.side_effect = ExternalServiceError('caida')
        servicio = CotizacionService(self.proveedor)
        for _ in range(2):
            with self.assertRaises(ExternalServiceError):
                servicio.tasa('COP')
        self.proveedor.obtener_tasa.assert_called_once_with('COP')


class TasaCambioAPITest(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.url = reverse('wallet:rate')

    def _autenticar(self):
        self.client.force_authenticate(UserService().register(username='tasa', email='tasa@example.com', password='vault-Test-4821'))

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_the_rate(self):
        self._autenticar()
        with mock.patch(URLOPEN, return_value=BytesIO(RESPUESTA_OK)):
            resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, {'moneda': 'COP', 'tasa': '3243.549'})

    def test_provider_outage_is_a_controlled_503(self):
        self._autenticar()
        with mock.patch(URLOPEN, side_effect=URLError('sin red')), self.assertLogs(level='WARNING'):
            resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(resp.data['code'], 'external_service_unavailable')


class WalletInitialCreditTest(TestCase):
    def test_initial_wallet_created_with_credit(self):
        svc = UserService()
        user = svc.register(username='bob', email='bob@example.com', password='strongpass')
        self.assertTrue(hasattr(user, 'billetera'))
        self.assertEqual(user.billetera.saldo, Decimal('1000.00'))


class WalletAPITestCase(APITestCase):
    def test_wallet_api_unauthorized_401(self):
        url = reverse('wallet:api_billetera_me')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wallet_api_authorized_200(self):
        user = UserService().register(username='ricardo', email='ricardo@example.com', password='vault-Test-4821')
        token, _ = Token.objects.get_or_create(user=user)

        url = reverse('wallet:api_billetera_me')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('saldo', resp.data)
        self.assertIn('transacciones', resp.data)
        self.assertEqual(resp.data['saldo'], '1000.00')
        self.assertEqual(len(resp.data['transacciones']), 1)
        self.assertEqual(resp.data['transacciones'][0]['tipo'], 'INICIAL')
        self.assertEqual(resp.data['transacciones'][0]['monto'], '1000.00')

