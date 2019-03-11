from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from  django.contrib.auth.hashers import make_password


# Create your views here.
# reference: https://medium.freecodecamp.org/user-authentication-in-django-bae3a387f77d
# https://docs.djangoproject.com/en/2.1/ref/contrib/auth/
# https://overiq.com/django-1-10/django-creating-users-using-usercreationform/
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = make_password(form.cleaned_data.get('password1'), salt=None, hasher='default')
            if not (User.objects.filter(username=username).exists()):
                user = User.objects.create(username=username, password=password, is_active=False) # set is_active false, so approval from server admin is needed
                author = Author.objects.create(user=user, host="http://natto.herokuapp.com")
                url_str = "http://natto.herokuapp.com/author/" + str(author.id)
                author.url = json.dumps(url_str)
                author.save()
                return HttpResponseRedirect('/signup/done/')
            else:
                raise forms.ValidationError('Looks like the username with that password already exists.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form' : form})

def signup_done(request):
    return render(request, 'registration/signup_done.html', {})

def home(request):
    return render(request, 'home.html', {'user_id':request.user.author.id})

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
def view_profile(request):
    return render(request, 'profile.html', {})
