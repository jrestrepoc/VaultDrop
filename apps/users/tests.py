from django.test import TestCase
from apps.users.services import UserService
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal


class UserRegistrationServiceTest(TestCase):
    def test_register_creates_user_and_wallet(self):
        svc = UserService()
        user = svc.register(username='alice', email='alice@example.com', password='strongpass')
        User = get_user_model()
        self.assertTrue(User.objects.filter(email='alice@example.com').exists())
        self.assertTrue(hasattr(user, 'billetera'))
        self.assertEqual(user.billetera.saldo, Decimal('1000.00'))


class UserRegistrationViewTest(TestCase):
    def test_register_view_success(self):
        url = reverse('users:register')
        resp = self.client.post(url, data={
            'username': 'carol',
            'email': 'carol@example.com',
            'password': 'securepass',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(email='carol@example.com').exists())

    def test_register_view_short_password(self):
        url = reverse('users:register')
        resp = self.client.post(url, data={
            'username': 'dave',
            'email': 'dave@example.com',
            'password': 'short',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(email='dave@example.com').exists())

    def test_register_view_duplicate_email(self):
        svc = UserService()
        svc.register(username='eve', email='eve@example.com', password='strongpass')
        url = reverse('users:register')
        resp = self.client.post(url, data={
            'username': 'eve2',
            'email': 'eve@example.com',
            'password': 'anotherstrong',
        })
        self.assertEqual(resp.status_code, 200)
        users = get_user_model().objects.filter(email='eve@example.com')
        self.assertEqual(users.count(), 1)
