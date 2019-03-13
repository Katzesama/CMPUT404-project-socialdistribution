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
    path('posts/<uuid:post_id>/', freeridersocial.Posts.get_one_post.as_view(), name="get_one_post"),
    path('addpost/', freeridersocial.Posts.upload_post.as_view(), name='add_post'),
    #path('delpost/', freeridersocial.views.del_post, name='del_post'),
    path('author/myPosts/', freeridersocial.Posts.my_post.as_view(), name='my_post'),
    path('posts/<uuid:post_id>/add_comments/', freeridersocial.Comments.addComment.as_view() , name='addcomment'),
    path('posts/<uuid:post_id>/comments/', freeridersocial.Comments.get_comments.as_view(), name='comments'),
]
