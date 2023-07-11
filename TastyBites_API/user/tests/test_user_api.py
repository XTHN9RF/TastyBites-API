"""
That file contains test cases for user api
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create_user')
LOGIN_USER_URL = reverse('user:login_user')
MANAGE_USER_URL = reverse('user:manage_user')


def create_user(**kwargs):
    """ Create user helper function test """
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """Test of the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test creating user with valid payload is successful """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword1',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test creating user that already exists fails """
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword1',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test that password must be more than 5 characters """
        payload = {
            'email': 'test@example.com',
            'password': 'p',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_token_created(self):
        """ Test that tokens are created when user is created """
        user_credentials = {
            'email': 'test@example.com',
            'password': 'testpassword1',
            'name': 'Test Name'
        }
        create_user(**user_credentials)

        payload = {
            'email': 'test@example.com',
            'password': 'testpassword1',
        }

        res = self.client.post(LOGIN_USER_URL, user_credentials)

        user = get_user_model().objects.get(email=user_credentials['email'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertIn('refresh_token', res.cookies)


class PrivateUserApiTests(TestCase):
    """Test cases for authenticated users features of the user API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpassword1',
            name='Test Name'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test retrieving profile for logged in user """
        res = self.client.get(MANAGE_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_not_allowed(self):
        """ Test that POST is not allowed on the manage user url """
        res = self.client.post(MANAGE_USER_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile for authenticated user """
        payload = {
            'name': 'New Name',
            'password': 'newpassword1'
        }

        res = self.client.patch(MANAGE_USER_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
