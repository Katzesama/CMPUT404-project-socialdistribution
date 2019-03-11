from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse


# http://service/posts/{post_id}/comments access to the comments in a post
# "query": "addComment"

def addComment(request, post_id):
    post = Post.objects.get(pk = post_id)
    current_user = request.user
    if request.method == "POST":
        #data = request.data
        comment = CommentSerializer(data=request.data['comment'], context={'author': current_user, 'postid':post_id})
        if comment.is_valid():
            comment.save()
            comment_data = {
                "query":"addComment",
                "success": True,
                "message": "Comment Added"
            }
            return Response(comment_data, status=Response.status.HTTP_200_OK)
    return Response({"query":"addComment", "success": False, "message": "Invalid Comment"}, status=Response.status.HTTP_400_BAD_REQUEST)

def deleteComment(request, comment_id):
    if request.method == "DELETE":
        try:
            comment = Comment.objects.get(id = comment_id)
            comment.delete()
            return HttpResponse(200)
        except:
            return HttpResponse(400)
