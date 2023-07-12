"""
File that handles the testing of the recipe api
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)

RECIPES_URL = reverse('recipe:recipe-list')


def generate_detail_url(recipe_id):
    """ Function that generates correct recipe detail url"""

    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Function that creates a recipe"""

    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': Decimal('5.00'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf'
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Function that creates a user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTest(TestCase):
    """Handles testing of public API features"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving recipes"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',
                                password='testpassword1',
                                name='Test User')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limiting_recipes_to_user(self):
        """Test that recipes returned are for authenticated user"""
        second_user = create_user(
            email='user2@example.com',
            password='testpassword2',
            name='Second User'
        )

        create_recipe(user=second_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_recipe_detail(self):
        """Test retrieving a recipe detail"""
        recipe = create_recipe(user=self.user)

        url = generate_detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe feature"""
        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 10,
            'price': Decimal('5.00'),
            'description': 'Sample Description',
            'link': 'http://example.com/recipe.pdf'
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial updating of recipe"""
        original_link = 'http://example.com/recipe.pdf'
        recipe = create_recipe(user=self.user, link=original_link, title='Sample Title')

        payload = {'title': 'Updated Title'}
        url = generate_detail_url(recipe.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Testing full update of recipe"""
        recipe = create_recipe(
            user=self.user,
            title='Sample Title',
            link='http://example.com/some.pdf',
            price=Decimal('5.85'),
            time_minutes=2
        )

        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 10,
            'price': Decimal('5.00'),
            'description': 'Sample Description',
            'link': 'http://example.com/recipe.pdf'
        }

        url = generate_detail_url(recipe.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_user_not_updating(self):
        """Test that user cannot be updated in recipe"""
        second_user = create_user(
            email='user2@example.com',
            password='testpassword2',
            name='Second User'
        )

        recipe = create_recipe(user=self.user)

        payload = {"user": second_user.id}
        url = generate_detail_url(recipe.id)

        res = self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test that user can delete recipe"""
        recipe = create_recipe(user=self.user)
        url = generate_detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_others_recipe(self):
        """Test that user cannot delete other user's recipe"""
        second_user = create_user(
            email='user2@example.com',
            password='testpassword2',
            name='Second User'
        )

        recipe = create_recipe(user=second_user)

        url = generate_detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
