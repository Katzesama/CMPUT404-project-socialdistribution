from .models import Author
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializer import AuthorSerializer

class ProfileDetail(APIView):

    def get(self, request):
        try:
            current_user_profile = request.user.author
        except:
            return Response("Can't find user", status=404)

        serializer = AuthorSerializer(current_user_profile)
        return Response(serializer.data)

class EditProfile(APIView):
    def post(self, request):
        try:
            serializer = AuthorSerializer(data = request.data)
        except:
            return Response("Invalid profile data", status = 400)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=200)

