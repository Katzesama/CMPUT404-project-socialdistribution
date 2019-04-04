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
"""
http://service/author/posts (posts that are visible to the currently authenticated user)
http://service/posts (all posts marked as public on the server)
-http://service/author/{AUTHOR_ID}/posts (all posts made by {AUTHOR_ID} visible to the currently authenticated user)
http://service/posts/{POST_ID} access to a single post with id = {POST_ID}
http://service/posts/{post_id}/comments access to the comments in a post
# ask a service GET http://service/author/<authorid>/friends/ if friend or not
# POST to http://service/author/<authorid>/friends ask a service if anyone in the list is a friend


"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
import freeridersocial.profile
import freeridersocial.views, freeridersocial.Posts, freeridersocial.Comments, freeridersocial.FriendRequest, freeridersocial.FriendList
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(), name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', freeridersocial.views.signup, name='signup'),
    path('signup/done/', freeridersocial.views.signup_done, name='registration_complete'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', freeridersocial.views.home, name='home'),
    path('author/<uuid:user_id>/', freeridersocial.profile.ProfileDetail.as_view(), name='profile'),
    path('author/<uuid:user_id>/editprofile/', freeridersocial.profile.EditProfile.as_view(),name = 'edit_profile'),

    path('author/posts/', freeridersocial.Posts.visible_post.as_view(), name='get_post_for_user_view'),
    path('posts/', freeridersocial.Posts.public_post.as_view(), name='public_posts_view'),
    path('author/myPosts/', freeridersocial.Posts.my_post.as_view(), name='my_post_view'),
    path('author/posts/views/', freeridersocial.views.get_visible_post_render, name='get_post_for_user'),
    path('posts/views/', freeridersocial.views.get_posts_render, name='public_posts'),
    path('author/myPosts/views/', freeridersocial.views.get_my_posts_render, name='my_posts'),
    path('author/<authorid>/api/', freeridersocial.profile.HandleProfile.as_view(), name = "handle_profile"),

    path('author/<uuid:authorid>/posts', freeridersocial.Posts.posts_from_an_author.as_view(), name='posts_from_an_author'),

    path('posts/<uuid:post_id>/', freeridersocial.Posts.get_one_post.as_view(), name="get_one_post"),
    path('addpost/', freeridersocial.Posts.upload_post.as_view(), name='add_post'),
    path('posts/<uuid:post_id>/del_post/', freeridersocial.Posts.del_post, name='del_post'),
    path('posts/<uuid:post_id>/edit_post/', freeridersocial.Posts.edit_post.as_view(), name='edit_post'),
    path('posts/<uuid:post_id>/comments/view/add_comment/', freeridersocial.Comments.addComment.as_view() , name='addcomment'),
    path('posts/<uuid:post_id>/comments/', freeridersocial.Comments.get_comments.as_view(), name='comments_view'),
    path('posts/<uuid:post_id>/comments/view/', freeridersocial.views.comments_render, name='comments'),

    path('friendrequest/', freeridersocial.FriendRequest.FriendRequestHandler.as_view(), name='friend_request_api'),
    path('friendrequest/view/', freeridersocial.views.FriendRequest_render, name='friend_requests'),
    path('author/<authorid1>/friends/<service2>/author/<authorid2>/', freeridersocial.FriendList.CheckIfFriend, name='check_if_friend'),
    path('friends/<friendid>/delete_friend/',freeridersocial.FriendList.DeleteFriend, name = 'delete_friend'),
    path('author/<authorid>/friends', freeridersocial.FriendList.FriendsOfAuthor, name='get_user_friends'),
    path('myfriends/', freeridersocial.FriendList.FriendList.as_view(), name= 'myfriends'),
    path('myfriends/views/', freeridersocial.views.FriendList, name= 'myfriends_render'),
    path('myfriends/views/<friendid>/delete/', freeridersocial.FriendList.DeleteFriend.as_view(), name= 'delete_friend'),
    path('updatefriend/', freeridersocial.FriendRequest.updateFriendRequestHandler.as_view(), name= 'update_friend_request'),
]
