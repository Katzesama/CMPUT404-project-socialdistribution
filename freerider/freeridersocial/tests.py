from django.test import TestCase
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
# Create your tests here.

class loginTest(TestCase):

    def setUp(self):
        password = make_password("12202stst")
        user = User.objects.create(username="TestUser", password=password)

    def test_login_success(self):

        response = self.client.login(username='TestUser', password='12202stst')
        self.assertTrue(response)

    def test_login_failed(self):

        response = self.client.login(username='TestUser', password='fake12202stst')
        self.assertFalse(response)

    def test_logout(self):
        self.client.login(username='TestUser', password='12202stst')
        response = self.client.logout()

        self.assertNotEqual(response.status_code, 200)


    

