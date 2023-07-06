"""
Tests for the models of the `core` app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Class that contains all the tests for the models of the `core` app."""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'test@example.com'
        password = 'testpassword1'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

