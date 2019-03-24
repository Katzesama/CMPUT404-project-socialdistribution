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
        # already_friend = False
        # proceeding = False
        # friends = FriendRequest.objects.filter(url = me.url) #data structure of friends?
        # for friend in friends:
        #     if friend.url == author_obj.url and friend.friend_status == "friend":
        #         already_friend = True
        #     elif friend.url == author_obj.url and friend.friend_status == "proceeding":
        #         proceeding == True
        # if already_friend:
        #     return HttpResponse("You two are already friends", status=403)
        # elif proceeding:
        #     return HttpResponse("Friend request is proceeding", status=403)

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

