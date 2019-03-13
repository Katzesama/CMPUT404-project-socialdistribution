from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Author
from django.test import Client
#from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# http://www.tomchristie.com/rest-framework-2-docs/api-guide/testing#example

class profile_test(TestCase):
    def setUp(self):
        user = User.objects.create(username = "testuser")
        user.set_password("huamao123")
        user.save()

        self.author = Author.objects.get(user = user)
        self.author.host = "http://127.0.0.1:8000/"
        self.author.displayName = "Dog"
        self.author.url = "http://127.0.0.1:8000/"
        self.author.github = "http://127.0.0.1:8000/"
        self.author.firstName = "Dog"
        self.author.email = "www.dog@gmail.com"
        self.author.bio = "1"
        self.author.save()
        #
        # self.client = APIClient()
        # self.client.force_authenticate(user=user)
        # response = self.client.get('/api/author/' + str(self.author.id) + '/')
        # self.responseCode = response.status_code
        # self.response = json.loads(response.content)

