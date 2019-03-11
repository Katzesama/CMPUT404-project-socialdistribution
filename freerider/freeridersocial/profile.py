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
        return Response({'serializer':serializer,'profile':current_user_profile, 'user_id':current_user_profile.id})

    def put(self, request, userid):
        try:
            current_user_profile = request.user.author
            author = get_object_or_404(Author.objects.get(id=userid))
            if author == current_user_profile:
                serializer = AuthorSerializer(current_user_profile, data = request.data)
                if serializer.is_valid(raise_exception=ValueError):
                    serializer.save()
                    return Response(serializer.data, status=200)
                return Response("serializer error", status=400)
            else:
                return Response(status=404)
        except:
            return Response(status = 400)

