"""freerider URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views

import freeridersocial.views
import freeridersocial.profile

import freeridersocial.views, freeridersocial.Posts, freeridersocial.Comments
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(), name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', freeridersocial.views.signup, name='signup'),
    path('signup/done/', freeridersocial.views.signup_done, name='registration_complete'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', freeridersocial.views.home, name='home'),
    path('author/<uuid:user_id>/', freeridersocial.profile.ProfileDetail.as_view(), name='profile'),
    path('author/<uuid:user_id>/editprofile', freeridersocial.profile.EditProfile.as_view(),name = 'edit_profile'),
    path('author/posts/', freeridersocial.Posts.visible_post.as_view(), name='get_post_for_user'),
    path('posts/', freeridersocial.Posts.public_post.as_view(), name='public_posts'),


    #path('addpost/', freeridersocial.views.upload_post, name='add_post'),
    #path('delpost/', freeridersocial.views.del_post, name='del_post'),
    #path('posts/<uuid:postid>/add_comments/', freeridersocial.views.addComment , name='addcomment'),
]
