from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_successfully(self):
        response = self.client.post('/auth/register', {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '1234567890',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')

    def test_login_user_successfully(self):
        User.objects.create_user(
            email='john@example.com',
            firstName='John',
            lastName='Doe',
            password='password123'
        )
        response = self.client.post('/auth/login', {
            'email': 'john@example.com',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')

    def test_missing_required_fields(self):
        response = self.client.post('/auth/register', {
            'firstName': '',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '1234567890',
        }, format='json')
        self.assertEqual(response.status_code, 422)

    def test_duplicate_email(self):
        User.objects.create_user(
            email='john@example.com',
            firstName='John',
            lastName='Doe',
            password='password123'
        )
        response = self.client.post('/auth/register', {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '1234567890',
        }, format='json')
        self.assertEqual(response.status_code, 422)
