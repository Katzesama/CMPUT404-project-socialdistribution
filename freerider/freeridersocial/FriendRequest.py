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
        me = self.request.user.author
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
        firend_request = Friend.objects.create(url=sender_url, friend_with=receiver, host=sender_host, displayName=sender_name)
        firend_request.friend_status = "proceeding"
        firend_request.save()
        return Response(status=200)
        #assume current user id contains host name
        #assume not friends yet
        #if me.url == receiver_url:

    def put(self, request):
        ''' (('friend','friend'),('proceeding','proceeding'),('rejected','rejected')) '''
        data = request.data
        receiver = Author.objects.filter(self.request.user.author)
        sender_url = data['sender_url']
        decision = data['decision']
        friend_request = Friend.objects.filter(url=sender_url, friend_with=receiver)
        if decision == 'accept':
            friend_request.friend_status = 'friend'
        elif decision == 'decline':
            friend_request.friend_status = 'rejected'
        friend_request.save()
        return Response(status=200)
        return Response(status=200)