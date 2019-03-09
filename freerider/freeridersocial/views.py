from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
# reference: https://medium.freecodecamp.org/user-authentication-in-django-bae3a387f77d
# https://docs.djangoproject.com/en/2.1/ref/contrib/auth/
# https://overiq.com/django-1-10/django-creating-users-using-usercreationform/
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            username = userObj['username']
            password =  userObj['password']
            if not (User.objects.filter(username=username).exists()):
                User.objects.create_user(username, password)
                user = authenticate(username = username, password = password, is_active = False) # set is_active false, so approval from server admin is needed
                return HttpResponseRedirect('/')
            else:
                raise forms.ValidationError('Looks like the username with that password already exists.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form' : form})

def signup_done(request):
    return render(request, 'registration/signup_done.html', {})

# http://service/author/{AUTHOR_ID}/posts (all posts made by {AUTHOR_ID} visible to the currently authenticated user)
# http://service/author/posts (posts that are visible to the currently authenticated user)
# http://service/posts (all posts marked as public on the server)
# http://service/posts/{POST_ID} access to a single post with id = {POST_ID}
def upload_post():
    return
def edit_post():
    return
def del_post():
    return
def get_post():
    return


def addComment(request, post_id):
    post = Post.objects.get(pk = post_id)
    current_user = request.user
    if request.method == "POST":
        #data = request.data
        comment = CommentSerializer(data=request.data['comment'], context={'author': current_user, 'postid':post_id})

        if comment.is_valid():
            comment.save()
            comment_data = {
                "query":"addComment",
                "success": True,
                "message": "Comment Added"
            }
            return Response(comment_data, status=Response.status.HTTP_200_OK)
    return Response({"query":"addComment", "success": False, "message": "Invalid Comment"}, status=Response.status.HTTP_400_BAD_REQUEST)

def deleteComment(request, comment_id):
    if request.method == "DELETE":
        try:
            comment = Comment.objects.get(id = comment_id)
            comment.delete()
            return HttpResponse(200)
        except:
            return HttpResponse(400)


# http://service/posts/{post_id}/comments access to the comments in a post
# "query": "addComment"

# a reponse if friends or not
# GET http://service/author/<authorid>/friends/
# Ask if 2 authors are friends
# GET http://service/author/<authorid>/friends/<authorid2>
# ---------
# ask a service if anyone in the list is a friend
# POST to http://service/author/<authorid>/friends
# Here GREG tries to get a post from LARA that's marked as FOAF visibility
# the server will query greg's server to ensure that he is friends with 7de and 11c
# then it will get the users from its own server and see if they are friends of Lara
# Then it will go to at least 1 of these friend's servers and verify that they are friends of Greg
# once it is verified via the 3 hosts that Greg is a friend, then greg will get the data for lara's post
# POST to http://service/posts/{POST_ID} , sending the body
#{
#	"query":"getPost",
# then this returns with the generic GET http://service/posts/{POST_ID}
# ----------
# to make a friend request, POST to http://service/friendrequest

# Profile API calls
# GET http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e
# Enables viewing of foreign author's profiles
