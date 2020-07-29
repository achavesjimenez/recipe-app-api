from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'u1@gmail.com',
            'password': '123456789',
            'name': 'Test user'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res_data = res.data
        user = get_user_model().objects.get(**res_data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res_data)

    def test_user_already_exists(self):
        """Test that fails when user already exists"""
        payload = {
            'email': 'u1@gmail.com',
            'password': '123456789',
            'name': 'Test user'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """test that fails when password is too small"""
        payload = {
            'email': 'u1@gmail.com',
            'password': '12',
            'name': 'Test user'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@londonappdev.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """tests that token not created when passing invalid credentials"""
        create_user(email='u1@gmail.com', password='123456789')
        payload = {
            'email': 'u1@gmail.com',
            'password': 'wrongPass',
            'name': 'test user'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that no token is issued when users does not exist"""
        payload = {
            'email': 'u1@gmail.com',
            'password': 'wrongPass',
            'name': 'test user'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """test that email and password are required for getting a token"""
        res = self.client.post(TOKEN_URL, {'email': 'u@gmail.com',
                                           'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
