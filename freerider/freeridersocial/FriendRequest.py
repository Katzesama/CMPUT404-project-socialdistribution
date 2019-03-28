from .models import Author, FriendRequest
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .serializer import FriendSerializer
import requests
import json

class FriendRequest(APIView):

    def get(self, request):
        '''get all friendrequest to me 前端可以了吗？'''
        me = self.request.user.author
        friendrequests = FriendRequest.objects.filter(friend_with = me, friend_status = "proceeding")
        serializer = FriendSerializer(friendrequests, many=True)

        return Response({'serializer': serializer.data})

    def post(self, request):
        # {
        #     "query": "friendrequest",
        #     "author": {
        #         "id": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
        #         "host": "http://127.0.0.1:5454/",
        #         "displayName": "Greg Johnson"
        #                        "url": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
        # },
        # "friend": {
        #     "id": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e637281",
        #     "host": "http://127.0.0.1:5454/",
        #     "displayName": "Lara Croft",
        #     "url": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
        #
        # }
        # }
        '''handle received friend request, when a button "accept" and "decline" is clicked what happen backend'''

        '''
        Idea:
        1. specify sender and receiver
        2. Check if friendrequest exist already
        3. If receiver sent a friendrequest to sender before, they automatically become friend
        4. Handle error case
        大问题： url是host + /author/ + uuid
        '''
        data = request.data
        if not data['query'] == 'friendrequest':
            return Response('Invalid request', status=status.HTTP_400_BAD_REQUEST)

        sender_url = data['author']['id']
        sender_obj = Author.objects.filter(url = sender_url)
        receiver_url = data['friend']['id']
        receiver_obj = Author.objects.filter(url = receiver_url)
        if FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, status="proceeding").exists():

            friend_request = FriendRequest.objects.filter(url = receiver_url, receiver = sender_obj, friend_status = "proceeding")
            friend_request.friend_status = 'friend'
            friend_request.save()
            return Response("Friend request sent", status=status.HTTP_200_OK)
        elif FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, status="Decline").exists():

            friend_request = FriendRequest.objects.filter(url=receiver_url, receiver=sender_obj, friend_status="declined")
            friend_request.friend_status = 'proceeding'
            friend_request.save()
            return Response("Friend request sent", status=status.HTTP_200_OK)

        elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="Decline").exists():

            friend_request = FriendRequest.objects.filter(url=sender_url, receiver=receiver_obj, friend_status="declined")
            friend_request.friend_status = 'proceeding'
            friend_request.save()
            return Response("Friend request sent", status=status.HTTP_200_OK)

        elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="proceeding").exists():

            return Response("Friend request already sent", status=status.HTTP_400_BAD_REQUEST)

        elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="friend").exists():

            return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)

        else:

            friend_request = FriendRequest.objects.create(url = sender_url, friend_with = receiver_obj, friend_status = 'proceeding')
            friend_request.save()
            return Response("Friend request sent", status=status.HTTP_200_OK)

    def put(self, request):
        '''
        貌似不需要这个了...
        Other server update the status of friendrequest 那local server呢？
        idea:
        1. friendrequest exist or not
        2. Local friendrequest or remote
        3. Assume request has attributes: sender_url

        '''
        data = request.data
        receiver = request.user.author
        sender_url = data['sender_url']
        decision = data['decision']
        friend_request = FriendRequest.objects.filter(url=sender_url, friend_with=receiver)

        '''if both authors are in local host'''
        sender = Author.objects.filter(url = sender_url)
        if receiver.host == sender.host:

            if decision == 'accept':
                friend_request.friend_status = "friend"
            elif decision == 'decline':
                friend_request.friend_status = "rejected"
            friend_request.save()

            return Response('local friendrequest updated',status=200)
        else:
            if decision == 'accept':
                friend_request.friend_status = "friend"
            elif decision == 'decline':
                friend_request.friend_status = "rejected"
            friend_request.save()

            return Response("remote status updated", status=200)




