from .models import Author
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer, FriendSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer

class ProfileDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Profile.html'
    def get(self, request, user_id, **kwargs):
        try:
            #print(user_id)
            current_user_profile = request.user.author
            author = get_object_or_404(Author, pk = user_id)
        except:
            return HttpResponse(status=404)

        serializer = AuthorSerializer(author)
        current_author = False
        if (current_user_profile.id == user_id):
            current_author = True
        return Response({'serializer':serializer.data, 'if_author': current_author})

        #handle follow user event
        # def post(self, request, user_id, **kwargs):
        #     author = get_object_or_404(Author, pk = user_id)
        #     current_user = request.user.author
        #     serializer = FriendSerializer(current_user)
        #     #check if already followed him


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

