from .models import Author, Friend
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer

class FriendRequest(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'FriendRequest.html'

    def get(self, request):
        my_id = request.user.id
