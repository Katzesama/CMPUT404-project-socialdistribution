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
import json

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
        #is_remote = check_if_request_is_remote(request)

        data = request.data

        # receiver = request.user.author
        # sender_url = data['friend_url']
        #
        # sender_url = sender_url.replace('"', '')

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
                print(connect_server.HostName)


        sender_url = data['author']['id']
        # sender_id = sender_url.replace(data['author']['host']+'author/', "")
        sender_id = UUID(sender_url.split('/author/')[1])
        print(sender_id)
        receiver_url = data['friend']['id']
        print('fuck')
        print(receiver_url)
        # receiver_id = receiver_url.replace(data['author']['host']+'author/', "")
        receiver_id = UUID(receiver_url.split('/author/')[1])


        '''Check if local has author objects corresponding to author and friend'''
        sender_exist = check_local_has_author(sender_id)
        receiver_exist = check_local_has_author(receiver_id)
        if not sender_exist:
            a = create_local_author(data['author'])
        if not receiver_exist:

            a = create_local_author(data['friend'])

        sender_obj = Author.objects.get(pk = sender_id)
        receiver_obj = Author.objects.get(pk = receiver_id)
        print(sender_obj.displayName)
        print(receiver_obj.displayName)
        fr = FriendRequest.objects.filter(url = receiver_url, friend_with=sender_obj, friend_status = 'proceeding')
        '''Check if two authors already friends'''

        is_friend = check_already_friends(sender_url, receiver_obj)
        if not is_friend:
            if FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, friend_status="proceeding").exists():
                    print('fuck this shit')
                    friend_request = FriendRequest.objects.filter(url = receiver_url, friend_with=sender_obj)[0]

                    friend_request.friend_status = 'friend'
                    friend_request.save()
                    resp = reply_remote_friendrequest(data, connect_server)
                    if resp.status_code != 200:
                        return Response('Friend request fail', status=status.HTTP_400_BAD_REQUEST)
                    return Response("Friend request sent", status=status.HTTP_200_OK)

            elif FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, friend_status="rejected").exists():
                print('no no not here')
                friend_request = FriendRequest.objects.filter(url = receiver_url, friend_with=sender_obj, friend_status='rejected')[0]
                friend_request.friend_status = 'proceeding'
                friend_request.save()
                return Response('friendrequest received', status=status.HTTP_200_OK)


            elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, friend_status="rejected").exists():

                friend_request = FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, friend_status='rejected')[0]
                friend_request.friend_status = 'proceeding'
                friend_request.save()
                return Response('friendrequest received', status=status.HTTP_200_OK)

            elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, friend_status="friend").exists():

                return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)

            elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, friend_status="proceeding").exists():
                return Response('friendrequest is processing', status=status.HTTP_400_BAD_REQUEST)
            else:
                print(receiver_obj)
                friend_request = FriendRequest.objects.create(id = receiver_obj.id,displayName= sender_obj.displayName,url = sender_url, friend_with=receiver_obj, friend_status= 'proceeding', host=sender_obj.host)
                friend_request.save()
                print('friend saved')
                return Response('Receive friendrequest', status=status.HTTP_200_OK)
        else:
            return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)

class updateFriendRequestHandler(APIView):
    def post(self, request):
        '''
        data['friend_url']
        data['decision']
        '''
        data = request.data

        me = request.user.author
        sender_url = data['friend_url']
        print(sender_url)
        sender_url = sender_url.replace('"','')
        sender_id = UUID(sender_url.split('/author/')[1])
        sender_obj = Author.objects.get(id = sender_id)
        sender_host = sender_obj.host


        '''Find which node is source of friend request'''
        nodes = ServerNode.objects.all()
        connect_server = None
        remote_tell_accept = False
        for node in nodes:
            if str(node.HostName)==sender_host:
                remote_tell_accept = True
                connect_server = node

        decision = data['decision']
        friend_request = FriendRequest.objects.filter(url = sender_url,friend_with=me, friend_status='proceeding')[0]
        if decision == 'accept':
            friend_request.friend_status = "friend"
            friend_request.save()

            if remote_tell_accept:
                request_form = {
                    "query": "friendrequest",
                    "author": {
                        'id': me.url,
                        'host': me.host,
                        'displayName': me.displayName,
                        'url': me.url,
                    },
                    "friend": {
                        'id': sender_obj.url,
                        'host': sender_host,
                        'displayName': sender_obj.displayName,
                        'url': sender_url,
                    }
                }
                resp = reply_remote_friendrequest(request_form, connect_server)

                if resp.status_code != 200:
                    return Response('Fail to send friendrequest back', status=status.HTTP_400_BAD_REQUEST)
        elif decision == 'decline':
            friend_request.friend_status = "rejected"
        friend_request.save()



        return Response(status=200)

#     def post(self, request):
#         # {
#         #     "query": "friendrequest",
#         #     "author": {
#         #         "id": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
#         #         "host": "http://127.0.0.1:5454/",
#         #         "displayName": "Greg Johnson"
#         #                        "url": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
#         # },
#         # "friend": {
#         #     "id": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e637281",
#         #     "host": "http://127.0.0.1:5454/",
#         #     "displayName": "Lara Croft",
#         #     "url": "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
#         #
#         # }
#         # }
#         '''handle received friend request, when a button "accept" and "decline" is clicked what happen backend'''
#
#         '''
#         Logic fixed
#         '''
#         check_authentication()
#         is_remote = check_if_request_is_remote(request)
#         data = request.data
#
#         # receiver = request.user.author
#         # sender_url = data['friend_url']
#         #
#         # sender_url = sender_url.replace('"', '')
#
#         if not data['query'] == 'friendrequest':
#             return Response('Invalid request', status=status.HTTP_400_BAD_REQUEST)
#
#         '''Find which node is source of friend request'''
#         nodes = ServerNode.objects.all()
#         connect_server = None
#         remote_tell_accept = False
#         for node in nodes:
#             if str(node.HostName) in data['friend']['host']:
#                 remote_tell_accept = True
#                 connect_server = node
#
#
#         sender_url = data['author']['id']
#         sender_id = sender_url.replace(data['author']['host']+'author/', "")
#         receiver_url = data['friend']['id']
#         receiver_id = receiver_url.replace(data['author']['host']+'author/', "")
#
#
#         '''Check if local has author objects corresponding to author and friend'''
#         sender_exist = check_local_has_author(sender_id)
#         receiver_exist = check_local_has_author(receiver_id)
#         if not sender_exist:
#             create_local_author(data['author'])
#         if not receiver_exist:
#             create_local_author(data['friend'])
#
#         sender_obj = Author.objects.get(pk = sender_id)
#         receiver_obj = Author.objects.get(pk = receiver_id)
#
#         '''Check if two authors already friends'''
#         is_friend = check_already_friends(sender_url, receiver_obj)
#         if not is_friend:
#             if FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, status="proceeding").exists():
#
#                     friend_request = FriendRequest.objects.filter(url = sender_url, friend_with=receiver_obj)[0]
#
#                     friend_request.friend_status = 'friend'
#                     friend_request.save()
#                     resp = reply_remote_friendrequest(data, connect_server)
#                     if resp.status_code != 200:
#                         return Response('Friend request fail', status=status.HTTP_400_BAD_REQUEST)
#                     return Response("Friend request sent", status=status.HTTP_200_OK)
#
#             elif FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, status="rejected").exists():
#
#                 friend_request = FriendRequest.objects.filter(url = receiver_url, friend_with=sender_obj, friend_status='rejected')[0]
#                 friend_request.friend_status = 'proceeding'
#                 friend_request.save()
#                 return Response('friendrequest received', status=status.HTTP_200_OK)
#
#
#             elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="rejected").exists():
#
#                 friend_request = FriendRequest.objects.filter(url=receiver_url, friend_with=sender_obj, friend_status='rejected')[0]
#                 friend_request.friend_status = 'proceeding'
#                 friend_request.save()
#                 return Response('friendrequest received', status=status.HTTP_200_OK)
#
#             elif FriendRequest.objects.filter(url=sender_url, friend_with=receiver_obj, status="friend").exists():
#
#                 return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)
#
#             else:
#                 friend_request = FriendRequest.objects.create(url = sender_url, friend_with=receiver_obj)
#                 friend_request.save()
#                 return Response('Receive friendrequest', status=status.HTTP_200_OK)
#         else:
#             return Response("Already friends", status=status.HTTP_400_BAD_REQUEST)
#
# class updateFriendRequestHandler(APIView):
#     def post(self, request):
#         '''
#         data['friend_url']
#         data['decision']
#         '''
#         data = request.data
#
#         me = request.user.author
#         sender_url = data['friend_url']
#
#         sender_url = sender_url.replace('"','')
#         sender_obj = Author.objects.filter(url = sender_url)[0]
#         sender_host = sender_obj.host
#
#
#         '''Find which node is source of friend request'''
#         nodes = ServerNode.objects.all()
#         connect_server = None
#         remote_tell_accept = False
#         for node in nodes:
#             if str(node.HostName)==sender_host:
#                 remote_tell_accept = True
#                 connect_server = node
#
#         decision = data['decision']
#         friend_request = FriendRequest.objects.filter(url = sender_url,friend_with=me, friend_status='proceeding')[0]
#         if decision == 'accept':
#             friend_request.friend_status = "friend"
#
#             if remote_tell_accept:
#                 request_form = {
#                     "query": "friendrequest",
#                     "author": {
#                         'id': me.id,
#                         'host': me.host,
#                         'displayName': me.displayName,
#                         'url': me.url,
#                     },
#                     "friend": {
#                         'id': sender_obj.id,
#                         'host': sender_host,
#                         'displayName': sender_obj.displayName,
#                         'url': sender_url,
#                     }
#                 }
#             resp = reply_remote_friendrequest(json.dumps(data), connect_server)
#             if resp.status_code != 200:
#                 return Response('Fail to send friendrequest back', status=status.HTTP_400_BAD_REQUEST)
#         elif decision == 'decline':
#             friend_request.friend_status = "rejected"
#         friend_request.save()
#
#
#
#         return Response(status=200)
