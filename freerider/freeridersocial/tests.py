from django.test import TestCase
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient

# Create your tests here.

class loginTest(TestCase):

    def setUp(self):       
        password = make_password("12202stst")
        User.objects.create(username="TestUser", password=password)

    def test_login_success(self):
        client = APIClient()
        response = client.login(username='TestUser', password='12202stst')
        self.assertTrue(response)

    def test_login_failed(self):
        client = APIClient()
        response = client.login(username='TestUser', password='fake12202stst')
        self.assertFalse(response)

    def test_logout(self):
        client = APIClient()
        client.login(username='TestUser', password='12202stst')
        # client.logout()
        response = client.get("/profile/")
        self.assertNotEqual(response.status_code, 200)


    

