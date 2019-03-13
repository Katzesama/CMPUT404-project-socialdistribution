# from django.test import TestCase
# from django.test import Client
# from django.contrib.auth.models import User
# from rest_framework.test import APIClient

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
# Create your tests here.

class loginTest(TestCase):

    def setup(self):
        self.client = Client()

    def test_logint(self):
        response = self.client.get("{% url 'login' %})
        self.assertEquals(response.status_code, 200)

