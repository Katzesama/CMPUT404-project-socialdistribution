from django.test import TestCase

from django.test import TestCase
from django.test import SimpleTestCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from freeridersocial.models import Author, Post, Comment
from freeridersocial.profile import *


# Create your tests here.

class loginTest(TestCase):

    def setUp(self):       
        password = make_password("12202stst")
        User.objects.create(username="TestUser", password=password)

    def test_login_success(self):
        response = self.client.login(username='TestUser', password='12202stst')
        self.assertTrue(response)

    def test_login_failed(self):
        response = self.client.login(username='TestUser', password='fake12202stst')
        self.assertFalse(response)

        response = self.client.login(username='TestUser1', password='12202stst')
        self.assertFalse(response)

    def test_logout(self):
        self.client.login(username='TestUser', password='12202stst')
        self.client.logout()
        response = self.client.get("/profile/")
        self.assertNotEqual(response.status_code, 200)



class profileTest(TestCase):

    def setUp(self):
        global author_id1, user_id1
        password1 = make_password("12202stst")
        user1 = User.objects.create(username="TestUser1", password=password1)
        user_id1 = user1.id
        author1 = Author.objects.create(user_id = user_id1)
        author_id1 = author1.id
        

        global author_id2, user_id2
        password2 = make_password("122ststst")
        user2 = User.objects.create(username="TestUser2", password=password2)
        user_id2 = user2.id
        author2 = Author.objects.create(user_id = user_id2)
        author_id2 = author2.id


    def test_profile_info(self):

        #client1 gets self profile
        self.client.login(username='TestUser1',password='12202stst')
        url = "http://127.0.0.1:8000/author/" + str(author_id1)
        response = self.client.get(url)
        self.assertTrue(response)
        self.client.logout()

        #client2 gets profile of client1
        self.client.login(username="TestUser2", password="122ststst")
        url = "http://127.0.0.1:8000/author/" + str(author_id1)
        response = self.client.get(url)
        self.assertTrue(response)

    def test_profile_update(self):

        author1 = Author.objects.get(user_id = user_id1)

        displayName = "TestUser1"
        github = "https://github.com/Katzesama/CMPUT404-project-socialdistribution"
        firstName = 'Project'
        lastName = "cmput404"
        author1.displayName = displayName
        author1.github = github
        author1.firstName = firstName
        author1.lastName = lastName
        author1.save()
        author1 = Author.objects.get(user_id = user_id1)

        self.assertEquals(author1.displayName,'TestUser1')
        self.assertEqual = (author1.github, "https://github.com/Katzesama/CMPUT404-project-socialdistribution")          
        self.assertNotEqual = (author1.firstName, "Assignment")
        self.assertNotEqual = (author1.lastName, "cmput466")

class post_comment_Test(TestCase):

    def setUp(self):
        global user_id1
        password1 = make_password("12202stst")
        user1 = User.objects.create(username="TestUser1", password=password1)
        user_id1 = user1.id
        author1 = Author.objects.create(user_id = user_id1)

        global author_id2, user_id2
        password2 = make_password("122ststst")
        user2 = User.objects.create(username="TestUser2", password=password2)
        user_id2 = user2.id
        author2 = Author.objects.create(user_id = user_id2)
        author_id2 = author2.id

    def test_post(self):
        author = Author.objects.get(user_id = user_id1)
        
        title = "First Post"
        content = "Test Post"
        description = "Testing"
        contentType = "text/plain"

        post = Post.objects.create(
            title = title,
            content = content,
            description = description,
            contentType = contentType,
            author = author
        )

        self.assertTrue(post)
        self.assertEqual(post.title, title)
        self.assertEqual(post.content, content)
        self.assertEqual(post.description, description)
        self.assertEqual(post.contentType, contentType)
        self.assertEqual(post.author, author)
        self.assertEqual(post.visibility, "PUBLIC")
    
    def test_self_comment(self):
        author = Author.objects.get(user_id = user_id1)

        post = Post.objects.create(
            content = "testing",
            author = author
        )

        comment = Comment.objects.create(
            post_id = post,
            comment = 'test comment',
            contentType = 'text/plain',
            author = author
        )

        self.assertEqual(comment.comment, "test comment")
        self.assertEqual(comment.post_id, post)
        self.assertEqual(comment.contentType, 'text/plain')
        self.assertEqual(comment.author, author)
        self.assertIsInstance(comment, Comment)


    def test_comment_to_others(self):
        author1 = Author.objects.get(user_id = user_id1)
        author2 = Author.objects.get(user_id = user_id2)

        post = Post.objects.create(
            content = "testing",
            author = author1
        )

        comment = Comment.objects.create(
            post_id = post,
            comment = 'test comment',
            contentType = 'text/plain',
            author = author2
        )

        self.assertEqual(comment.comment, "test comment")
        self.assertEqual(comment.post_id, post)
        self.assertEqual(comment.contentType, 'text/plain')
        self.assertEqual(comment.author, author2)
        self.assertIsInstance(comment, Comment)
