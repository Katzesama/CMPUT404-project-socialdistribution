from .models import Author, FriendRequest
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
from .serializer import FriendSerializer

class FriendRequest(APIView):
    def get(self, request):
        author_id = self.request.user.id
        me = Author.objects.get(pk = author_id)
        friendrequests = FriendRequest.objects.filter(friend_with = me, friend_status = "proceeding")
        serializer = FriendSerializer(friendrequests, many=True)

        return Response({'serializer': serializer.data})

    def post(self, request):
        '''handle received friend request'''
        data = request.data
        receiver = Author.objects.filter(url=data['friend']['url'])
        sender_url = data['author']['url']
        sender_host = data['author']['host']
        sender_name = data['author']['displayName']
        friend_request = Friend.objects.create(url=sender_url, friend_with=receiver, host=sender_host, displayName=sender_name)
        friend_request.friend_status = "proceeding"
        friend_request.save()
        return Response(status=200)
        #assume current user id contains host name
        #assume not friends yet
        #if me.url == receiver_url:

    def put(self, request):
        return Response(status=200)
