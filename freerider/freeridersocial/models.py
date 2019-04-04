# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import uuid
import json

# Profile With User
class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False, null=True, blank=True)
    host = models.URLField()
    displayName = models.CharField(max_length=200,blank=False,null=False)
    url = models.URLField(editable=False)
    github = models.URLField(null=True, blank=False)
    firstName = models.CharField(max_length=200,blank=True,default='')
    lastName = models.CharField(max_length=200,blank=True,default='')
    email = models.CharField(max_length=400,blank=True,default='')
    bio = models.CharField(max_length=2000,blank=True,default='')
    image = models.ImageField(null=True, blank=True, upload_to="profile_pics")

    def __str__(self):  # __unicode__ for Python 2
        return self.displayName

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length = 100, default='No Title')
    source = models.CharField(max_length = 2000)
    origin = models.CharField(max_length = 2000, editable=False)
    description = models.CharField(max_length =100)
    contentType_choice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base65'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    image = models.ImageField(null=True, blank=True)
    contentType = models.CharField(max_length=2000, choices=contentType_choice, default='text/markdown')
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    published = models.DateTimeField(default=datetime.now)
    categories = models.TextField(null=True, blank=True)

    visibility_choice = (
        ('PUBLIC', 'PUBLIC'),
        ('FOAF', 'FOAF'),
        ('FRIENDS', 'FRIENDS'),
        ('PRIVATE', 'PRIVATE'),
        ('SERVERONLY', 'SERVERONLY'),
    )
    visibility = models.CharField(default ="PUBLIC", max_length=20, choices=visibility_choice)
    visibleTo = models.TextField(null=True, blank=True)
    unlisted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Images(models.Model):
	associated_post = models.ForeignKey(Post, on_delete=models.CASCADE)
	img = models.ImageField(null=True, blank=True)

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id= models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment =  models.TextField(max_length =2000)
    contentType_choice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base65'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    contentType = models.CharField(max_length=2000, default='text/plain', choices=contentType_choice)
    published = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author.displayName + ": " + self.comment

class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displayName = models.CharField(max_length=200,blank=True)
    host = models.URLField(blank=True)
    url = models.URLField()
    friend_with = models.ForeignKey(Author, related_name="request_sender", on_delete=models.CASCADE)
    status = (('friend','friend'),('proceeding','proceeding'),('rejected','rejected'),)
    friend_status = models.CharField(max_length=50, choices=status, default='proceeding')
    def __str__(self):
        return self.displayName

class ServerNode(models.Model):
    HostName = models.URLField(primary_key=True, default="")
    auth_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='node', null=True, blank=True)
    Image_visibility = models.BooleanField(default=True)
    Post_visibility = models.BooleanField(default=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)

