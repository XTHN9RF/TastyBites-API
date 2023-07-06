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

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@exampLe.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for sample_email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(
                email=sample_email,
                password='samplepassword1'
            )

            self.assertEqual(user.email, expected_email)

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='samplepassword1'
            )

    def test_creating_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser('test@example.com', 'samplepassword1')

        self.assertTrue(user.is_superuser)
