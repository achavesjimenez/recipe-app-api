from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test tags public api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'u@gmail.com',
            '123456'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test retrieving tags"""
        Tag.objects.create(name='Vegan', user=self.user)
        Tag.objects.create(name='Dessert', user=self.user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        expected = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected.data)

    def test_retrieve_only_authenticated_user_tags(self):
        """test that only tags from the authenticated user are returned"""

        user2 = get_user_model().objects.create_user(
            'u2@gmail.com',
            '123456'
        )
        Tag.objects.create(name='Fish', user=user2)
        tag = Tag.objects.create(name='Vegan', user=self.user)
        expected = TagSerializer(tag).data
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0], expected)
