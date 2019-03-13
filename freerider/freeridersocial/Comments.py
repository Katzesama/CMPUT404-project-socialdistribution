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


# http://service/posts/{post_id}/comments access to the comments in a post
# "query": "addComment"

class addComment(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'addcomment.html'
    def get(self, request, post_id, **kwargs):
        try:
            current_user_profile = request.user.author
            self.post = get_object_or_404(Post, pk = post_id)
        except:
            return HttpResponse(status=404)
        self.new_comment = Comment.objects.create(post_id=self.post, author=current_user_profile)
        serializer = CommentSerializer(self.new_comment)
        return Response({"serializer": serializer})

    def post(self, request, post_id, **kwargs):
        serializer = CommentSerializer(self.new_comment, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("", self.post.id)

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
        pg_obj = PaginationModel()
        pg_res = pg_obj.paginate_queryset(queryset=comment_list, request=request)
        res = CommentSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)
