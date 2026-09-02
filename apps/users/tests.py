import os
from unittest import mock

from django.test import TestCase
from apps.users.services import UserService
from apps.users.domain.builders import UserBuilder
from apps.users.infra.factories import NotificadorFactory, NotificadorConsola, NotificadorEmail
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

    def test_login_view_success(self):
        UserService().register(username='login-user', email='login-user@example.com', password='strongpass')
        url = reverse('users:login')
        resp = self.client.post(url, data={
            'username': 'login-user',
            'password': 'strongpass',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.endswith(reverse('core:home')))

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

    def test_register_view_duplicate_username(self):
        svc = UserService()
        svc.register(username='ivan', email='ivan1@example.com', password='strongpass')
        url = reverse('users:register')
        resp = self.client.post(url, data={
            'username': 'ivan',
            'email': 'ivan2@example.com',
            'password': 'anotherstrong',
        })
        # No debe reventar con un 500 (IntegrityError): el form vuelve a
        # renderizarse con el error de negocio.
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'nombre de usuario ya está en uso')
        self.assertFalse(get_user_model().objects.filter(email='ivan2@example.com').exists())


class UserServiceDuplicateDataTest(TestCase):
    def test_register_with_duplicate_username_raises_value_error(self):
        svc = UserService()
        svc.register(username='julia', email='julia1@example.com', password='strongpass')
        with self.assertRaisesMessage(ValueError, 'El nombre de usuario ya está en uso'):
            svc.register(username='julia', email='julia2@example.com', password='strongpass')

    def test_register_with_duplicate_email_raises_value_error(self):
        svc = UserService()
        svc.register(username='karen', email='karen@example.com', password='strongpass')
        with self.assertRaisesMessage(ValueError, 'El correo ya está registrado'):
            svc.register(username='karen2', email='karen@example.com', password='strongpass')


class UserBuilderTest(TestCase):
    def test_build_success_returns_valid_unsaved_user(self):
        user = (
            UserBuilder()
            .con_username('frank')
            .con_email('frank@example.com')
            .con_password('strongpass')
            .build()
        )
        self.assertIsNone(user.pk)
        self.assertEqual(user.username, 'frank')
        self.assertEqual(user.email, 'frank@example.com')
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('strongpass'))

    def test_build_with_short_password_raises_value_error(self):
        with self.assertRaises(ValueError):
            (
                UserBuilder()
                .con_username('gina')
                .con_email('gina@example.com')
                .con_password('short')
                .build()
            )

    def test_build_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            (
                UserBuilder()
                .con_username('hugo')
                .con_password('strongpass')
                .build()
            )


class NotificadorFactoryTest(TestCase):
    @mock.patch.dict(os.environ, {'NOTIFICACION_MODE': 'MOCK'})
    def test_crea_notificador_consola_en_modo_mock(self):
        notificador = NotificadorFactory.crear()
        self.assertIsInstance(notificador, NotificadorConsola)

    @mock.patch.dict(os.environ, {'NOTIFICACION_MODE': 'REAL'})
    def test_crea_notificador_email_en_modo_real(self):
        notificador = NotificadorFactory.crear()
        self.assertIsInstance(notificador, NotificadorEmail)

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_modo_por_defecto_es_mock_si_no_hay_variable_de_entorno(self):
        notificador = NotificadorFactory.crear()
        self.assertIsInstance(notificador, NotificadorConsola)
