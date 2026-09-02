from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from decimal import Decimal

from apps.users.services import UserService


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
        user = UserService().register(username='ricardo', email='ricardo@example.com', password='password123')
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

