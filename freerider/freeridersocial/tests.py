from django.test import TestCase
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from freeridersocial.models import Author
from django.test import Client

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


class profileTest(TestCase):

    def setUp(self):
        global user_id1, user_id2
        password = make_password("12202stst")
        user = User.objects.create(username="TestUser1", password=password)
        user_id1 = user.id

        password = make_password("122ststst")
        user = User.objects.create(username="TestUser2", password=password)
        user_id2 = user.id

    def test_profile_info(self):
        client = APIClient()
        client.login(username='TestUser1', password="12202stst")
        author = Author.objects.create(user_id = user_id1)

        author = Author.objects.get(user_id = user_id1)
        self.assertTrue(author)
        self.assertEqual(author.user_id, user_id1)
        client.logout()

        #test TestUser2 can view TestUser1's profile
        client.login(username='TestUser2', password="122ststst")
        author = Author.objects.get(user_id = user_id1)
        self.assertTrue(author)

    def test_profile_update(self):

        client = APIClient()
        client.login(username='TestUser1', password="12202stst")
        author = Author.objects.create(user_id = user_id1)
        
        Author.displayName = "TestUser1"
        Author.github = "https://github.com/Katzesama/CMPUT404-project-socialdistribution"
        Author.firstName = 'Project'
        Author.lastName = "cmput404"
        updateProfile = Author.objects.get(user_id = user_id1)
        self.assertTrue(author)
        self.assertEqual = (updateProfile.user_id, user_id1)
        self.assertEqual = (updateProfile.displayName, "TestUser1")
        self.assertEqual = (updateProfile.github, "https://github.com/Katzesama/CMPUT404-project-socialdistribution")  
        client.logout()
        
        #login TestUser2 to see if the TestUser1's profile successfully changed
        client.login(username='TestUser2', password="122ststst")
        author = Author.objects.get(user_id = user_id1)
        self.assertEqual = (author.firstName, "Project")
        self.assertEqual = (author.lastName, "cmput404")



