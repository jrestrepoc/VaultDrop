from django.test import TestCase
from apps.users.services import UserService
from decimal import Decimal


class WalletInitialCreditTest(TestCase):
    def test_initial_wallet_created_with_credit(self):
        svc = UserService()
        user = svc.register(username='bob', email='bob@example.com', password='strongpass')
        self.assertTrue(hasattr(user, 'billetera'))
        self.assertEqual(user.billetera.saldo, Decimal('1000.00'))
