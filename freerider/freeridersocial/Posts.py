from .models import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import *
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
import uuid

# http://service/author/{AUTHOR_ID}/posts (all posts made by {AUTHOR_ID} visible to the currently authenticated user)
# http://service/author/posts (posts that are visible to the currently authenticated user)
# http://service/posts (all posts marked as public on the server)
# http://service/posts/{POST_ID} access to a single post with id = {POST_ID}

# reference: https://blog.csdn.net/u013210620/article/details/79856682
# reference: https://www.django-rest-framework.org/topics/html-and-forms/
# https://www.cnblogs.com/wdliu/p/9142832.html

# https://docs.djangoproject.com/en/2.1/topics/http/sessions/

class visible_post(APIView):
    def get(self, request, format=None):
        posts = []
        try:
            #print(user_id)

            current_user_profile = request.user.author
        except:
            return HttpResponse(status=404)
        posts = Post.objects.filter(visibility='PUBLIC')
        posts_only_visible = Post.objects.filter(visibleTo__contains = current_user_profile.url)
        posts += posts_only_visible
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)

class public_post(APIView):
    def get(self, request, format=None):
        posts = Post.objects.filter(visibility='PUBLIC')
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)

class upload_post(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'addpost.html'
    def get(self, request, **kwargs):
        try:
            #print(user_id)
            current_user_profile = request.user.author
        except:
            return HttpResponse(status=404)
        new_post = Post.objects.create(author=current_user_profile)
        serializer = PostSerializer(new_post)
        request.session["new_post_id"] = str(new_post.id)
        return Response({"serializer": serializer})

    def post(self, request, **kwargs):
        #try:
            #print("not here")
            #author = get_object_or_404(Author.objects.get(id=userid))
            #if author == current_user_profile:
        #print("aaaaaaaa"+str(preserve_id))
        try:
            #id = request.session["new_post_id"]
            id = uuid.UUID(request.session['new_post_id']).hex
            new_post = Post.objects.get(id=id)
        except:
            new_post = Post.objects.create(author=request.user.author)
        serializer = PostSerializer(new_post, data = request.data)
        if serializer.is_valid():
            print("what's the matter")
            serializer.save()
            # return Response({'serializer':serializer, 'profile': current_user_profile})
            return redirect("get_one_post", new_post.id)
        return JsonResponse({'serializer': serializer.data})

class my_post(APIView):
    def get(self, request, format=None):
        try:
            #print(user_id)
            current_user_profile = request.user.author
        except:
            return HttpResponse(status=404)
        posts = Post.objects.filter(author=current_user_profile)
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        print(res.data)
        return pg_obj.get_paginated_response(res.data)


class get_one_post(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'onePost.html'
    def get(self, request, post_id, **kwargs):
        try:
            print("get here")
            post = get_object_or_404(Post, pk = post_id)
        except:
            return HttpResponse(status=404)
        serializer = PostSerializer(post)
        return Response({"serializer": serializer.data})
