from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@provider.com', '123')
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@provider.com',
            password="123",
            name='Test user full name'
        )

    def test_user_listed(self):
        """test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)  # perform http

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_page_change_works(self):
        """test that the user edit page works correctly"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """create user page works correctly"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
