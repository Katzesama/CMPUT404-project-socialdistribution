from .models import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer, FriendSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
import requests, json
from rest_framework import status
from collections import OrderedDict
from .tools import *
from rest_framework import status
from django.core import serializers
from django.contrib.auth.models import User, AnonymousUser
from uuid import UUID

# Profile API calls
# GET http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e
# Enables viewing of foreign author's profiles
#
# Response
#{
  # "id":"http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
  # "host":"http://127.0.0.1:5454/",
  # "displayName":"Lara",
  # "url":"http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
  # "friends": [
  #   {
  #     "id":"http://127.0.0.1:5454/author/8d919f29c12e8f97bcbbd34cc908f19ab9496989",
  #     "host":"http://127.0.0.1:5454/",
  #     "displayName":"Greg",
  #     "url": "http://127.0.0.1:5454/author/8d919f29c12e8f97bcbbd34cc908f19ab9496989"
  #   }
  # ],
class HandleProfile(APIView):
    '''api: handle get an author's profile request'''

    def get(self, request, authorid):
        #if request.user.is_authenticated:
        #     remote_user = request.user
        #     node = ServerNode.objects.filter(source = remote_user)[0]
        #     remote_host = node.HostName
        # else:
        #     return Response('unidentified user', status=403)
        print('in handle profile')
        check_authentication()
        print('pass auth')
        is_remote = check_if_request_is_remote(request)
        print('isremote'+ str(is_remote))

        # try:
        author = get_object_or_404(Author, pk=UUID(authorid))
        print(author.displayName)
        host = author.host
        id = host + '/author/'+str(author.id)
        displayName = author.displayName
        url = id
        friendlist = []
        friendrequests = FriendRequest.objects.filter(url = author.url)
        for friendrequest in friendrequests:
            if friendrequest.friend_status == 'friend':
                friend = friendrequest.friend_with
                frienddict = {}
                frienddict['id'] = friend.url
                frienddict['host'] = friend.host
                frienddict['displayName'] = friend.displayName
                frienddict['url'] = friend.url
                friendlist.append(frienddict)

        response = {
            'id': id,
            'host': host,
            'displayName': displayName,
            'url': url,
            'friends':friendlist,
        }

        return Response(response,status=status.HTTP_200_OK)


        # except:
        #     return Response(status=404)


class ProfileDetail(APIView):
    '''
    check if author is remote, if so send request for author data
    '''

    check_authentication()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Profile.html'
    def get(self, request, user_id, **kwargs):
        #Only handles local request, check if local has author, otherwise send request to get his profile
        try:
            author = Author.objects.get(id = user_id)
        except:
            return Response("author does not exist", status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author)
        current_author = False
        me = request.user.author
        if (me.id == user_id):
            current_author = True
            return Response({'serializer':serializer.data, 'if_author': True, 'able_friend': False})

        able_friend = True
        friendrequests = FriendRequest.objects.filter(url = me.url, friend_with = author)
        for friendrequest in friendrequests:
            try:
                friendrequest.friend_status == 'friend'
                able_friend = False
            except:
                pass

            try:
                friendrequest.friend_status == 'proceeding'
                able_friend = False
            except:
                pass

        return Response({'serializer':serializer.data, 'if_author': current_author, 'able_friend': able_friend})

    def post(self, request, user_id, **kwargs):

        '''if locally add friend'''
        # is_remote = check_if_request_is_remote(request)
        is_remote_user = True
        my_host = request.scheme + '://'+ request.get_host()
        print('my_host: '+ my_host)
        if Author.objects.filter(host = my_host).exists():
            for author in Author.objects.filter(host = my_host):
                author_id = author.id
                if user_id == author_id:
                    is_remote_user = False
        print('is remote?', str(is_remote_user))
        if not is_remote_user:
            author = Author.objects.get(id = user_id)
            me = request.user.author
            friendrequest = FriendRequest.objects.create(displayName=me.displayName, host=me.host, url=me.url, friend_with=author, friend_status='proceeding')
            friendrequest.save()
            serializer = AuthorSerializer(author)
            return Response({'serializer': serializer.data, 'if_author': False, 'able_friend': False})
            #TODO 前端发个消息：friendrequest已发送

        author = Author.objects.get(id = user_id)
        remote_host = author.host #"http://127.0.0.1:5454/"
        # if remote_host == 'http://natto.herokuapp.com':
        #     remote_host = request.scheme + '://127.0.0.1:8000'
        print('remote host' + remote_host)
        me = request.user.author
        node = ServerNode.objects.get(HostName = remote_host)
        username = node.username
        pwd = node.password
        # print('username'+username)
        # print('aaaaaaaaa')
        # print(remote_host)
        # print(request.scheme + '://' + request.get_host())
        # if remote_host == request.scheme + '://' + request.get_host():
            #print('im inside')

        author = Author.objects.filter(id = user_id)[0]
        friendrequest = FriendRequest.objects.create(displayName=me.displayName, host=me.host, url=me.url, friend_with=author, friend_status='proceeding')
        friendrequest.save()




        url = remote_host + '/friendrequest/'
        print(url)
        author = Author.objects.filter(id = user_id)[0]
        request_body = {
            "query": 'friendrequest',
            "author": {
                    "id": me.url,
                    "url": me.url,
                    "host": me.host,
                    "displayName": me.displayName,
                },
                "friend": {
                    "id": author.url,
                    "url": author.url,
                    "host": author.host,
                    "displayName": author.displayName,
                },
            }
        authentication = HTTPBasicAuth(node.username, node.password)
        resp = requests.post(url, data=json.dumps(request_body), auth = authentication,
                             headers={'Content-Type': 'application/json'})
        #Handle error case
        # if resp['success'] == False:
        #     error_message = resp['message']

        serializer = AuthorSerializer(author)

        return Response({'serializer': serializer.data, 'if_author': False, 'able_friend': False})


class EditProfile(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'EditProfile.html'

    def get(self, request, **kwargs):
        try:
            current_user_profile = request.user.author
        except:
            return HttpResponse(status=404)

        serializer = AuthorSerializer(current_user_profile)

        return Response({'serializer':serializer,'profile':current_user_profile})

    def post(self, request, **kwargs):
        current_user_profile = request.user.author
        serializer = AuthorSerializer(current_user_profile, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("profile", current_user_profile.id)

        print(serializer.errors)
        return Response({'serializer': serializer, 'profile': current_user_profile})
