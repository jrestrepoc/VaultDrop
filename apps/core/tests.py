from django.test import TestCase
from django.urls import reverse

from apps.users.services import UserService


class HomeViewTest(TestCase):
    def test_home_responds_ok_for_anonymous_user(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'VaultDrop')
        self.assertContains(resp, reverse('users:register'))

    def test_home_greets_authenticated_user(self):
        UserService().register(username='hank', email='hank@example.com', password='strongpass')
        self.client.login(username='hank', password='strongpass')
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'hank')
        self.assertContains(resp, reverse('users:dashboard'))
