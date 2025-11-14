from django.test import TestCase
from core.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class UserModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_unique_user_with_email(self):
        """Test that creating a user with an existing email raises IntegrityError"""
        email = 'test@example.com'
        password = 'testpass123'
        User.objects.create_user(email=email, password=password)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email=email, password='anotherpass')

    def test_create_user_without_email_raises_error(self):
        """Test creating a user without an email raises an error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='test123')

    def test_create_superuser_successful(self):
        """Test creating a superuser"""
        email = 'admin@example.com'
        password = 'adminpass123'
        user = User.objects.create_superuser(email=email, password=password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_email_is_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'Test@Example.com'
        user = User.objects.create_user(email=email, password='pass123')
        self.assertEqual(user.email, 'test@example.com')

    def test_user_str_method(self):
        """Test the string representation of the user"""
        user = User.objects.create_user(email='strtest@example.com', password='pass')
        self.assertEqual(str(user), 'strtest@example.com')