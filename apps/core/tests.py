from django.test import TestCase
from django.urls import reverse

from apps.users.services import UserService


class HomeViewTest(TestCase):
    def test_home_is_available_without_authentication(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'vaultdrop-app')
        self.assertContains(resp, 'data-authenticated="false"')
        self.assertContains(resp, 'data-register-url')

    def test_home_greets_authenticated_user(self):
        UserService().register(username='hank', email='hank@example.com', password='strongpass')
        self.client.login(username='hank', password='strongpass')
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'hank')
        self.assertContains(resp, reverse('users:dashboard'))
