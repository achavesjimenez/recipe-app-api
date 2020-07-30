from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """creates and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_authorized_user_needed_for_recipe_resource(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'u@gmail.com',
            '123456'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        expected_data = RecipeSerializer(recipes, many=True).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)

    def test_only_user_recipes_retrieved(self):
        """test that only authenticated user recipes are retrieved"""
        user2 = get_user_model().objects.create_user(
            'u2@gmail.com',
            '123456'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        expected_data = RecipeSerializer(recipes, many=True).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, expected_data)
