from .models import *
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
from .tools import *
import requests
import json
from django.contrib.auth.models import User, AnonymousUser

class FriendRequestHandler(APIView):

    def get(self, request):
        '''get all friendrequest to me 前端可以了吗？'''
            #current_user_id = get_current_user_id(request)
        if request.user.is_authenticated:
            pass
        else:
            return Response('unidentified user', status=403)

        current_author = request.user.author
        friendrequests = FriendRequest.objects.filter(friend_with = current_author, friend_status = "proceeding")
        serializer = FriendSerializer(friendrequests, many=True)
        serializer_list = []
        for s in serializer.data:
            serializer_list.append(s)
        print(serializer_list)
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
        Logic fixed
        '''
        check_authentication()
        is_remote = check_if_request_is_remote(request)
        data = request.data

        if not data['query'] == 'friendrequest':
            return Response('Invalid request', status=status.HTTP_400_BAD_REQUEST)

        '''Find which node is source of friend request'''
        nodes = ServerNode.objects.all()
        connect_server = None
        remote_tell_accept = False
        for node in nodes:
            if str(node.HostName) in data['friend']['host']:
                remote_tell_accept = True
                connect_server = node


        sender_url = data['author']['id']
        sender_id = sender_url.replace(data['author']['host']+'author/', "")
        receiver_url = data['friend']['id']
        receiver_id = receiver_url.replace(data['author']['host']+'author/', "")


        '''Check if local has author objects corresponding to author and friend'''
        sender_exist = check_local_has_author(sender_id)
        receiver_exist = check_local_has_author(receiver_id)
        if not sender_exist:
            create_local_author(data['author'])
        if not receiver_exist:
            create_local_author(data['friend'])

        sender_obj = Author.objects.get(pk = sender_id)
        receiver_obj = Author.objects.get(pk = receiver_id)

        '''Check if two authors already friends'''
        is_friend = check_already_friends(sender_url, receiver_obj)
        if not is_friend:
            if FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, status="proceeding").exists():

                friend_request = FriendRequest.objects.filter(url = receiver_url, receiver = sender_obj, friend_status = "proceeding")
                friend_request.friend_status = 'friend'
                friend_request.save()
                if remote_tell_accept:
                    reply_remote_friendrequest(data, connect_server)

            elif FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, status="Decline").exists():

                friend_request = FriendRequest.objects.filter(url=receiver_url, receiver=sender_obj, friend_status="declined")
                friend_request.friend_status = 'proceeding'
                friend_request.save()
                if remote_tell_accept:
                    reply_remote_friendrequest(data, connect_server)
                return Response("Friend request sent", status=status.HTTP_200_OK)

            elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="Decline").exists():

                friend_request = FriendRequest.objects.filter(url=sender_url, receiver=receiver_obj, friend_status="declined")
                friend_request.friend_status = 'proceeding'
                friend_request.save()
                if remote_tell_accept:
                    reply_remote_friendrequest(data, connect_server)
                return Response("Friend request sent", status=status.HTTP_200_OK)

            elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="proceeding").exists():

                return Response("Friend request already sent", status=status.HTTP_400_BAD_REQUEST)

            elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="friend").exists():

                return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)

            else:

                return Response('Something is wrong when receiving friendrequest', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)

class UpdateFriendRequestHandler(APIView):
    def post(self, request):
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
        if decision == 'accept':
            friend_request.friend_status = "friend"
        elif decision == 'decline':
            friend_request.friend_status = "rejected"
        friend_request.save()
        return Response(status=200)
        return Response(status=200)
