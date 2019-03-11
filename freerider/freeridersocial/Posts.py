from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse

# http://service/author/{AUTHOR_ID}/posts (all posts made by {AUTHOR_ID} visible to the currently authenticated user)
# http://service/author/posts (posts that are visible to the currently authenticated user)
# http://service/posts (all posts marked as public on the server)
# http://service/posts/{POST_ID} access to a single post with id = {POST_ID}

# reference: https://blog.csdn.net/u013210620/article/details/79856682
# reference: https://www.django-rest-framework.org/topics/html-and-forms/
# https://www.cnblogs.com/wdliu/p/9142832.html
class visible_post(APIView):
    posts = []
    posts = Post.objects.filter(visibility='PUBLIC')
    posts_only_visible = Post.objects.filter()
    def get(self, request, format=None):
        return 

class public_post(APIView):
    def get(self, request, format=None):
        posts = Post.objects.filter(visibility='PUBLIC')
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)

def upload_post():
    return
def del_post():
    return
