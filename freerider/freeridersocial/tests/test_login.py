from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
# Idea on test login: https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests

class LoginTestCase(TestCase):

    global user_id

    def setUp(self):
        user = User.objects.create(username="Laoshu")
        user.set_password('Huamao123')
        user.save()
        user_id = user.id

    def login_false(self):
        user = User.objects.get(id = user_id)
        c = Client
        logged_in = c.login(username = 'Laoshu', password = 'Laoshu123')
        self.assertFalse(logged_in)

    def login_true(self):
        user = User.objects.get(id=user_id)
        c = Client()
        logged_in = c.login(username='Laoshu', password='Huamao123')
        #response = self.client.login(username='Laoshu', password='Laoshu123')
        self.assertTrue(logged_in)

    def test_invalid_log_in(self):
        response = self.client.login(username='Houzi', password='Laoshu123')

        self.assertFalse(response, "invalid user logged in")