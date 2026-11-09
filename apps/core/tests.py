from django.test import TestCase, override_settings
from django.urls import reverse

from apps.users.services import UserService


class HomeViewTest(TestCase):
    def test_home_is_available_without_authentication(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'vaultdrop-app')
        self.assertContains(resp, 'data-authenticated="false"')
        self.assertContains(resp, 'data-register-url')

    @override_settings(CATALOG_URL='')
    def test_catalog_url_defaults_to_django_without_gateway(self):
        self.assertContains(self.client.get(reverse('core:home')), f'data-catalog-url="{reverse("cases:list")}"')

    @override_settings(CATALOG_URL='/api/v2/catalogo/')
    def test_catalog_url_uses_microservice_behind_gateway(self):
        self.assertContains(self.client.get(reverse('core:home')), 'data-catalog-url="/api/v2/catalogo/"')

    def test_home_greets_authenticated_user(self):
        UserService().register(username='hank', email='hank@example.com', password='strongpass')
        self.client.login(username='hank', password='strongpass')
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'hank')
        self.assertContains(resp, reverse('users:logout'))

    def test_logout_ends_the_session(self):
        UserService().register(username='hank', email='hank@example.com', password='strongpass')
        self.client.login(username='hank', password='strongpass')
        resp = self.client.post(reverse('users:logout'))
        self.assertRedirects(resp, reverse('core:home'))
        self.assertNotIn('_auth_user_id', self.client.session)
