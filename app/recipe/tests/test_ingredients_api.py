from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to access ingredient resource"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test for private ingredients methods"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'u@gmail.com',
            '123456'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """test retrieving the list of ingredients"""
        Ingredient.objects.create(user=self.user, name="Beef")
        Ingredient.objects.create(user=self.user, name="Cod")

        res = self.client.get(INGREDIENTS_URL)

        # ordered by name in reverse order
        all_ingredients = Ingredient.objects.all().order_by('-name')
        expected_data = IngredientSerializer(all_ingredients, many=True).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, expected_data)

    def test_only_authenticated_user_ingredients_retrieved(self):
        """test that only ingredients from the authenticated user are
           retrieved
        """
        user2 = get_user_model().objects.create_user(
            'u2@gmail.com',
            '123456'
        )

        ingredient = Ingredient.objects.create(user=self.user, name='Apple')
        Ingredient.objects.create(user=user2, name='Guinness')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0], IngredientSerializer(ingredient).data)

    def test_create_ingredient_success(self):
        """test that a ingredient is added to the list"""
        payload = {
            'name': 'Beef'
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Ingredient.objects.all().filter(
            name=payload['name']
        ).exists()
        self.assertEqual(exists, True)

    def test_create_ingredient_malformed_payload(self):
        """Test that a bad request is returned when ingredient
           payload is incorrect
        """
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
