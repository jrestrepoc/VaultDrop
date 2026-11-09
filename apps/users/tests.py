import os
from smtplib import SMTPException
from unittest import mock

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.services import UserService
from apps.users.domain.builders import UserBuilder
from apps.users.infra.factories import NotificadorFactory, NotificadorConsola, NotificadorEmail
from apps.users.tasks import NotificadorEnCola, tarea_bienvenida, tarea_envio_simulado
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


class FormulariosAccesiblesTest(TestCase):
    def test_registro_ayuda_al_navegador_y_enlaza_con_login(self):
        resp = self.client.get(reverse('users:register'))
        self.assertContains(resp, 'autocomplete="new-password"')
        self.assertContains(resp, 'autocomplete="email"')
        self.assertContains(resp, f'href="{reverse("users:login")}"')

    def test_login_usa_la_contrasena_guardada(self):
        self.assertContains(self.client.get(reverse('users:login')), 'autocomplete="current-password"')


class NotificacionesEnColaTest(TestCase):
    def setUp(self):
        self.user = UserService().register(username='cola', email='cola@example.com', password='strongpass')

    def test_publica_solo_el_id_para_el_worker(self):
        with mock.patch('apps.users.tasks.tarea_bienvenida.delay') as delay:
            NotificadorEnCola().enviar_bienvenida(self.user)
        delay.assert_called_once_with(self.user.pk, 'es')

    def test_tarea_usa_el_notificador_configurado(self):
        with mock.patch('apps.users.tasks.NotificadorFactory.crear') as crear:
            tarea_envio_simulado(self.user.pk, 'AK-47')
        crear.return_value.enviar_envio_simulado.assert_called_once_with(self.user, 'AK-47')

    def test_correo_sale_en_el_idioma_de_quien_lo_pidio(self):
        with mock.patch('apps.users.infra.factories.send_mail') as enviar, mock.patch.dict(os.environ, {'NOTIFICACION_MODE': 'REAL'}):
            tarea_bienvenida(self.user.pk, 'en')
        self.assertEqual(enviar.call_args.kwargs['subject'], 'Welcome to VaultDrop!')
        self.assertIn('cola', enviar.call_args.kwargs['message'])

    def test_fallo_de_correo_llega_a_celery_y_se_reintenta(self):
        with mock.patch('apps.users.infra.factories.send_mail', side_effect=SMTPException('caido')) as enviar, \
                mock.patch.dict(os.environ, {'NOTIFICACION_MODE': 'REAL'}):
            resultado = tarea_bienvenida.apply(args=[self.user.pk])
        self.assertTrue(resultado.failed())
        self.assertEqual(enviar.call_count, 4)


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


class UserAPITestCase(APITestCase):
    def test_weak_passwords_are_rejected(self):
        for password in ('12345678', 'password123', 'weakuser1'):
            data = {'username': 'weakuser1', 'email': 'weak@example.com', 'password': password}
            resp = self.client.post(reverse('users:api_register'), data, format='json')
            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, password)
        self.assertFalse(get_user_model().objects.filter(username='weakuser1').exists())

    def test_email_longer_than_its_column_is_rejected(self):
        email = 'a' * 60 + '@' + ('b' * 60 + '.') * 4 + 'com'
        data = {'username': 'longmail', 'email': email, 'password': 'strongpass'}
        resp = self.client.post(reverse('users:api_register'), data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_api_success_201(self):
        url = reverse('users:api_register')
        payload = {
            'username': 'juanperez',
            'email': 'juan@example.com',
            'password': 'supersecretpassword123',
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', resp.data)
        self.assertIn('user', resp.data)
        self.assertEqual(resp.data['user']['username'], 'juanperez')
        self.assertEqual(resp.data['user']['email'], 'juan@example.com')

        User = get_user_model()
        user = User.objects.get(username='juanperez')
        self.assertTrue(hasattr(user, 'billetera'))
        self.assertEqual(user.billetera.saldo, Decimal('1000.00'))

    def test_register_api_duplicate_username_409(self):
        UserService().register(username='clon', email='clon1@example.com', password='vault-Test-4821')
        url = reverse('users:api_register')
        payload = {
            'username': 'clon',
            'email': 'clon2@example.com',
            'password': 'vault-Test-4821',
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', resp.data)

    def test_register_api_duplicate_email_409(self):
        UserService().register(username='user1', email='repetido@example.com', password='vault-Test-4821')
        url = reverse('users:api_register')
        payload = {
            'username': 'user2',
            'email': 'repetido@example.com',
            'password': 'vault-Test-4821',
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', resp.data)

    def test_register_api_short_password_400(self):
        url = reverse('users:api_register')
        payload = {
            'username': 'shortpass',
            'email': 'shortpass@example.com',
            'password': '123',
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', resp.data)

    def test_login_api_success_200(self):
        UserService().register(username='logintest', email='login@example.com', password='vault-Test-4821')
        url = reverse('users:api_login')
        payload = {
            'username': 'logintest',
            'password': 'vault-Test-4821',
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'logintest')

    def test_login_api_invalid_credentials_400(self):
        UserService().register(username='loginbad', email='loginbad@example.com', password='vault-Test-4821')
        url = reverse('users:api_login')
        payload = {
            'username': 'loginbad',
            'password': 'wrongpassword',
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', resp.data)

