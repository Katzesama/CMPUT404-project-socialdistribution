from .models import *
from .serializer import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer, FriendSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
import uuid


# http://service/posts/{post_id}/comments access to the comments in a post
# "query": "addComment"

class addComment(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'addcomment.html'
    def get(self, request, post_id, **kwargs):
        try:
            current_user_profile = request.user.author
            post = get_object_or_404(Post, pk = post_id)
        except:
            return HttpResponse(status=404)
        new_comment = Comment.objects.create(post_id=post, author=current_user_profile)
        request.session["Comment_id"] = str(new_comment.id)
        serializer = CommentSerializer(new_comment)
        return Response({"serializer": serializer})

    def post(self, request, post_id, **kwargs):

        post = get_object_or_404(Post, pk = post_id)
        try:
            id = uuid.UUID(request.session['Comment_id']).hex
            new_comment = Comment.objects.get(id=id)
        except:
            new_comment = Comment.objects.create(post_id = post, author=request.user.author)
        serializer = CommentSerializer(new_comment, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("get_one_post", post.id)

        print("awsl")
        print(serializer.errors)
        return Response({'serializer': serializer})

# POST to http://service/posts/{POST_ID}/comments
class get_comments(APIView):
    def get(self, request, post_id, **kwargs):
        try:
            post = get_object_or_404(Post, pk = post_id)
        except:
            return HttpResponse(status=404)
        comment_list = Comment.objects.filter(post_id=post)
        pg_obj = PaginationModel()
        pg_res = pg_obj.paginate_queryset(queryset=comment_list, request=request)
        res = CommentSerializer(pg_res, many=True)
        print(res.data)
        return pg_obj.get_paginated_response(res.data)
