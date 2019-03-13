from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse


# http://service/posts/{post_id}/comments access to the comments in a post
# "query": "addComment"

class addComment(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'addcomment.html'
    post = None
    new_comment = None
    def get(self, request, post_id, **kwargs):
        try:
            current_user_profile = request.user.author
            post = get_object_or_404(Post, pk = post_id)
        except:
            return HttpResponse(status=404)
        new_comment = Comment.objects.create(post_id=post, author=current_user_profile)
        serializer = CommentSerializer(new_comment)
        return Response({"serializer": serializer})

    def post(self, request, post_id, **kwargs):
        serializer = CommentSerializer(new_comment, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("", post.id)

        print("awsl")
        print(serializer.errors)
        return Response({'serializer': serializer})

class get_comments(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'comments.html'
    def get(self, request, post_id, **kwargs):
        try:
            post = get_object_or_404(Post, pk = post_id)
        except:
            return HttpResponse(status=404)
        comment_list = Comment.objects.filter(post_id=post)
        serializer = CommentSerializer(new_comment)
        return Response({"serializer": serializer})
