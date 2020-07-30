from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='user@gmail.com', password='123456'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating user with an email is successful"""
        email = "email@provider.com"
        password = "123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test email has been normalized after its creation"""
        email = 'email@PROVIDER.COM'
        user = get_user_model().objects.create_user(email, '123')

        self.assertEqual(user.email, email.lower())

    def test_email_validation_is_performed(self):
        """tests that emil validation is performed"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '123')

    def test_superuser_created(self):
        """test creating a new super user"""
        user = get_user_model().objects.create_superuser(
            'super@provider.com', '123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_string_tag_representation(self):
        """test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_string_representation(self):
        """test the representation of a ingredient"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_string_representation(self):
        """test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Paella',
            time_minutes=25,
            price=10.00
        )

        self.assertEqual(str(recipe), recipe.title)
