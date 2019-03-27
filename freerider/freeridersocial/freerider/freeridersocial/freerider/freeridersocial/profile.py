from .models import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer, FriendSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
import requests
from rest_framework import status
from collections import OrderedDict
from rest_framework import status

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
    '''handle get an author's profile request'''
    def get(self, request, authorid):
        try:
            author = get_object_or_404(Author, pk=authorid)
            # serializer = AuthorSerializer(author)
            # return JsonResponse(serializer.data)
            host = author.host + '/'
            id = host + 'author/'+author.id
            displayName = author.displayName
            url = id
            response = OrderedDict([
                ('id', id),
                ('host', host),
                ('displayName', displayName),
                ('url', url),
            ])

            # friends = FriendRequest.objects.filter(url=author.url)
            # friendlist = list()
            # for friend in friends:
            #     author_id = authorid  # de305d54-75b4-431b-adb2-eb6b9e546013
            #     friend_url = friend.url  # 127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
            #     friend_id = friend_url.replace(friend.host, "")
            #     friend_host = friend.host
            #     url = author.url
            #     try:
            #         url = url.replace('https://', "")
            #     except:
            #         url = url.replace('http://', '')
            #     url = url.replace(str(author_id), '')
            #
            #     if not friend_host.endwith("/"):
            #         friend_host += '/'
            #
            #     url_content = friend_host + 'author/' + friend_id + '/friends/' + url + '/author/' + str(author_id)
            #     if not url_content.endwith('/'):
            #         url_content += '/'
            #     resp = requests.get(url_content, headers={'Content-Type': 'application/json'})
            #     if json.loads(resp.content).get('friends'):
            #         friendlist.append(friend)
            #         friend.friend_status = "friend"
            #         friend.save()
            return Response(response,status=status.HTTP_200_OK)


        except Exception as e:
            return HttpResponse(status=404)


class ProfileDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Profile.html'
    def get(self, request, user_id, **kwargs):
        try:
            current_user_profile = request.user.author
            author = get_object_or_404(Author, pk = user_id)
        except:
            return HttpResponse(status=404)

        serializer = AuthorSerializer(author)
        current_author = False
        if (current_user_profile.id == user_id):
            current_author = True

        '''Check friend status, if proceeding or friend, make front-end button(addFriend) unclickable'''
        able_friend = True
        friends = FriendRequest.objects.filter(url = current_user_profile.url)
        for friend in friends:
            if friend.url == author.url and friend.friend_status == "friend":
                able_friend = False

            elif friend.url == author.url and friend.friend_status == "proceeding":
                able_friend == False

        return Response({'serializer':serializer.data, 'if_author': current_author, 'able_friend': able_friend})

    def post(self, request, author_obj, **kwargs):
        renderer_classes = [TemplateHTMLRenderer]
        template_name = 'Profile.html'
        '''Check pre-request of friend request'''
        me = request.user.author

        '''proceed friend request'''
        host = author_obj.url.split('/author/')[0]
        request_url = host + "/friendrequest"
        data = {
            "query": 'friendrequest',
            "author": {
                "id": me.url,
                "url": me.url,
                "host": me.host,
                "displayName": me.displayName,
            },
            "friend": {
                "id": author_obj.url,
                "url": author_obj.url,
                "host": host,
                "displayName": author_obj.displayName,
            },
        }
        '''save friend object'''
        friendRequest = FriendRequest.objects.create(url = me.url, friend_with = author_obj.url, friend_status = "proceeding")
        friendRequest.save()


        '''send friend request out to the foreign host'''
        resp = requests.post(author_obj.host, data=json.dumps(data), auth=(author_obj.host.username, author_obj.host.password),
        headers={'Content-Type': 'application/json'})

        return Response("Friend request sent", status=status.HTTP_200_OK)













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

