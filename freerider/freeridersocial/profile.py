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
from rest_framework import status
from django.core import serializers
from django.contrib.auth.models import User, AnonymousUser

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
        if request.user.is_authenticated:
            pass
        else:
            return Response('unidentified user', status=403)

        try:
            author = get_object_or_404(Author, pk=authorid)
            # serializer = AuthorSerializer(author)
            # return JsonResponse(serializer.data)
            host = author.host + '/'
            id = host + 'author/'+author.id
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

            return Response(json.dumps(response),status=status.HTTP_200_OK)


        except:
            return Response(status=404)


class ProfileDetail(APIView):
    '''
    本地author可以吗？好像可以。。。
    1. render author info to front-end
    2. check if local has user as author object, if not store it
    3. check if friend
    4. check if its my own profile
    '''


    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Profile.html'
    def get(self, request, user_id, **kwargs):
        '''require user_id to be an url'''
        # nodes = ServerNode.objects.all()
        # for node in nodes:
        #     username = node.username
        #     pwd = node.password
        #     remote_url = node.HostName + 'author/' +user_id + '/'
        #
        #     global foundProfile
        #     foundProfile = False
        #     author = {}
        #
        #     try:
        #         resp = requests.get(remote_url, auth=(username,pwd))
        #         author = json.loads(resp.text)
        #         author['id'] = user_id
        #         foundProfile = True
        #     except:
        #         pass
        #
        #     if foundProfile:
        #         remote_host = node.HostName
        #
        #         break
        author = Author.objects.filter(id=user_id)
        # author_friend = AuthorSerializer(data=author)
        # author_friend.is_valid(raise_exception=True)
        # author_friend.save()
            #Save author locally
        author = Author.objects.filter(id = user_id)
        serializer = AuthorSerializer(author)
        current_author = False
        print("i am here")
        me = request.user.author
        if (me.id == user_id):
            current_author = True
            return Response({'serializer':serializer.data, 'if_author': True, 'able_friend': False})

        able_friend = True
        friendrequests = FriendRequest.objects.filter(url = me.url)
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

    def post(self, request, profile_id, **kwargs):
        '''
        1. Local friendrequest?
        2. Should already has author in local
        3. Authentication
        '''

        nodes = self.UserNode.objects.all()
        for node in nodes:
            username = node.username
            pwd = node.password
            remote_url = node.HostName + 'author/' + profile_id + '/'

            global foundProfile
            foundProfile = False
            author = {}

            try:
                resp = requests.get(remote_url, auth=(username, pwd))
                author = json.loads(resp.text)
                author['id'] = profile_id
                foundProfile = True
            except:
                pass

            if foundProfile:
                remote_host = node.HostName

                break

        me = request.user.author

        '''if locally add friend'''
        if remote_host == 'http://' + request.get_host() + '/':
            author = Author.objects.filter(id = profile_id)
            friendrequest = FriendRequest.objects.create(id=me.url, displayName=me.displayName, host=me.host, url=me.url, friend_with=author, friend_status='proceeding')
            friendrequest.save()
            serializer = AuthorSerializer(author)
            return Response({'serializer': serializer.data, 'if_author': False, 'able_friend': False})



        url = remote_host + '/friendrequest/'
        author = Author.objects.filter(id = profile_id)
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
        resp = requests.post(url, data=json.dumps(request_body), auth = (username, pwd),
                             headers={'Content-Type': 'application/json'})
        friendrequest = FriendRequest.objects.create(id=me.url, displayName=me.displayName, host=me.host, url=me.url, friend_with=author, friend_status='proceeding')
        #Handle error case
        if resp['success'] == False:
            error_message = resp['message']
            #前端打出error message
        friendrequest.save()

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


# def get_current_user_id(request):
#     if request.user.is_authenticated:
#         try:
#             User.objects.filter(pk=request.user.id)
#         except:
#             return Response('unidentified user', status=404)
#
#         current_user = User.objects.get(pk=request.user.id)
#         try:
#             Author.objects.filter(user =current_user)
#         except:
#             return Response('unidentified author object', status=404)
#
#         author = get_object_or_404(Author, user=current_user)
#         return author.id


