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
from django.shortcuts import render, redirect

class FriendList(APIView):
    '''get friend of mine'''
    def get(self, request):
        current_user = request.user.author
        friends_as_sender = FriendRequest.objects.filter(url = current_user.url, friend_status = "friend")
        friends_as_receiver = FriendRequest.objects.filter(friend_with = current_user.url, friend_status = "friend")
        friends = friends_as_sender + friends_as_receiver #list + list

        return render(request, "DisplayFriends.html",{'author': current_user, 'friends': friends})

    def delete(self, request, friend_id, **kwargs):
        '''check if friend exist'''
        try:
            me = request.user.author
            friend = FriendRequest.objects.filter(url = me.url, friend_status = "friend")
            friend.delete()
            return HttpResponse("friend is deleted", status=200)
        except:
            HttpResponse("friend object doesn't exist", status=404)





