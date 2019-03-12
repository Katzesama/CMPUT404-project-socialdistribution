from .models import Author
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer

class ProfileDetail(APIView):
    # renderer_classes = (JSONRenderer, )
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'Profile.html'
    def get(self, request,*args, **kwargs):
        print(*args)
        try:
            current_user_profile = request.user.author
            #author = get_object_or_404(Author, pk = pk)
        except:
            return HttpResponse(status=404)

        serializer = AuthorSerializer(current_user_profile)
        #print(serializer.data)
        return Response({'serializer':serializer.data})

class EditProfile(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'EditProfile.html'

    def get(self, request, **kwargs):
        try:
            current_user_profile = request.user.author
            #author = get_object_or_404(Author, pk = pk)
        except:
            return HttpResponse(status=404)

        serializer = AuthorSerializer(current_user_profile)
        #print(serializer.data)
        return JSONResp({'serializer':serializer,'profile':current_user_profile})

    def post(self, request, **kwargs):
        #try:
            #print("not here")
        current_user_profile = request.user.author
            #author = get_object_or_404(Author.objects.get(id=userid))
            #if author == current_user_profile:
        serializer = AuthorSerializer(current_user_profile, data = request.data)
        print(request.data)
        if serializer.is_valid():
            print('valid!!!!!!!!!')
            serializer.save()
            # return Response({'serializer':serializer, 'profile': current_user_profile})
            return redirect("profile", current_user_profile.id)

        print("awsl")
        print(serializer.errors)
        return Response({'serializer': serializer, 'profile': current_user_profile})


        #raise Exception as e:
            # print(e)
            # return HttpResponse(status = 400)

