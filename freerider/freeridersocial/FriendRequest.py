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
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'FriendRequest.html'
    def get(self, request):
        author_id = self.request.user.id
        me = Author.objects.get(pk = author_id)
        friendrequests = FriendRequest.objects.filter(friend_with = me, friend_status = "proceeding")
        serializer = FriendSerializer(friendrequests, many=True)

        return Response({'serializer': serializer.data})

    def post(self, request):
        '''handle received friend request'''
        data = request.data

        me = Author.objects.get(pk = self.request.user.id)
        sender_url = data['author']['id']
        receiver_url = data['friend']['id']

        #assume current user id contains host name
        #assume not friends yet
        #if me.url == receiver_url:



