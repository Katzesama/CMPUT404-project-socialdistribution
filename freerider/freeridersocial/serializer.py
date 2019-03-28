from .models import *
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict


# serializers
# reference: https://www.django-rest-framework.org/api-guide/serializers/
# https://docs.djangoproject.com/en/2.1/topics/serialization/
# https://www.jianshu.com/p/9e19ee78d3cc

# pagination
# reference: https://www.cnblogs.com/wdliu/p/9142832.html
# https://www.django-rest-framework.org/api-guide/pagination/

# reference: https://docs.djangoproject.com/en/2.0/ref/request-response/
# https://www.django-rest-framework.org/api-guide/fields/

class PaginationModel(PageNumberPagination):
    page_size = 50
    # Client can control the page using this query parameter.
    page_query_param = 'page'
    # Client can control the page size using this query parameter.
    page_size_query_param = 'size'
    # Set to an integer to limit the maximum page size the client may request.
    max_page_size = None

    def get_paginated_response(self, data):
        if "comments" in self.request.path:
            type = "comments"
        else:
            type = "posts"
        response_body = OrderedDict([
            ("query", type),
            ('count', self.page.paginator.count),
            ("size", self.page_size),
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            (type, data)
        ])

        if self.get_previous_link() is None:
            del response_body["previous"]
        if self.get_next_link() is None:
            del response_body["next"]
        return Response(response_body)

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"

class FriendSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False)
    class Meta:
        model = FriendRequest
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    contentType = serializers.ChoiceField(choices=Post.contentType_choice)
    visibility = serializers.ChoiceField(choices=Post.visibility_choice)
    class Meta:
        model = Post
        fields = ("title", "source", "origin", "description", "contentType", "content",
            "author", "categories", "count", "size", "next", "comments", "published", "id", "visibility",
            "visibleTo", "unlisted")

    def get_comments(self, obj):
        comments = Comment.objects.filter(post_id=obj.id).order_by('published')
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    def get_count(self, obj):
        counts = Comment.objects.filter(post_id=obj.id).order_by('published').count()
        return counts

    def get_size(self, obj):
        return 50

    def get_next(self, obj):
        return obj.author.host + '/posts/' + str(obj.id) + '/comments'


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    contentType = serializers.ChoiceField(choices=Comment.contentType_choice)
    class Meta:
        model = Comment
        fields = "__all__"
