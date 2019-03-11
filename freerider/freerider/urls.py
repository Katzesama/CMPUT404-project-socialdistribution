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
import profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(), name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', freeridersocial.views.signup, name='signup'),
    path('signup/done/', freeridersocial.views.signup_done, name='registration_complete'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', freeridersocial.views.home, name='home'),
    #path('author/<uuid:user_id>/', freeridersocial.views.view_profile, name='profile'),
    path('author/<uuid:user_id>/', profile.ProfileDetail.as_view(), name='profile'),
    path('author/posts/', freeridersocial.views.visible_post, name='get_post_for_user'),
    path('posts/<uuid:postid>/add_comments/', freeridersocial.views.addComment , name='addcomment'),
    path('posts/', freeridersocial.views.visible_post, name='public_posts')

]
