import requests

from .models import *

def get_author_viewable_post(author, posts):
    viewable_posts = list()
    for post in posts:
        if authorized_to_view(author, post):
            viewable_posts.append(post)
    return viewable_posts

def get_following_list(author):
    friendrequests = FriendRequest.objects.filter(url = author.url)
    for friendrequest in friendrequests:
        if friendrequest.friend_status =

def authorized_to_view(author, post):
    if author.user.is_superuser:
        return True
        # Public
    if post['visibility'] == "PUBLIC":
        return True
        # Own
    if str(post['author']['id']) == str(author.id):
        return True
        # Private
    if post['visibility'] == "PRIVATE":
        if str(author.id) in post['visibleTo']:
            return True

    local_post = Post.objects.get(id=post['id'])
    if authorized_to_view_local(author, local_post):
        return True
    else:
        if post['visibility'] == 'FRIENDS':
            try:
                friendrequests = FriendRequest.objects.filter(url = author.url)
                for friendrequest in friendrequests:
                    if
                author.following.get(id=post['author']['id'])
                return is_following(post['author']['host'], post['author']['id'], author.url)
            except:
                return False


def check_if_two_are_friends(host, poster_id, viewer_url):

