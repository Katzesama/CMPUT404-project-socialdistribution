from .models import *
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import *
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
from uuid import UUID
from django.db.models import F
from .tools import *
from django.core import serializers

# http://service/author/{AUTHOR_ID}/posts (all posts made by {AUTHOR_ID} visible to the currently authenticated user)
# http://service/author/posts (posts that are visible to the currently authenticated user)
# http://service/posts (all posts marked as public on the server)
# http://service/posts/{POST_ID} access to a single post with id = {POST_ID}

# reference: https://blog.csdn.net/u013210620/article/details/79856682
# reference: https://www.django-rest-framework.org/topics/html-and-forms/
# https://www.cnblogs.com/wdliu/p/9142832.html

# https://docs.djangoproject.com/en/2.1/topics/http/sessions/


'''
# http://service/author/posts (posts that are visible to the currently authenticated user)
'''
class visible_post(APIView):
    #author/posts/
    def get(self, request, format=None):
        # if request.user.is_authenticated:
        #     pass
        # else:
        #     return Response('unidentified user', status=403)
        # posts = []
        # try:
        #     #print(user_id)
        #     current_user_profile = request.user.author
        #     if not current_user_profile:
        #         return HttpResponse(status=404)
        # except:
        #     return HttpResponse(status=404)
        # public_posts = Post.objects.filter(visibility='PUBLIC', unlisted=False)
        # posts_only_visible = Post.objects.filter(visibleTo__contains = current_user_profile.url)
        # posts = public_posts | posts_only_visible
        check_authentication()
        is_remote = check_if_request_is_remote(request)
        local_posts = []
        remote_posts = []
        if is_remote:
            try:
                user_id = request.META.get('HTTP_X_REQUEST_USER_ID', '')
                current_author = Author.objects.get(pk=user_id)
            except:
                return Response('remote user uuid not found', status=404)
        if not is_remote:
            current_author = Author.objects.get

            #Get all posts posted by current user
            if Post.objects.filter(author = current_author).exist():
                for post in Post.objects.filter(author=current_author):
                    local_posts.append(post)

            #Get all public posts in local server
            if Post.objects.filter(visibility='PUBLIC').exist():
                for post in Post.objects.filter(visibility="PUBLIC"):
                    local_posts.append(post)

            #Get all posts sent by local friend
            local_friends = []
            if FriendRequest.objects.filter(url = current_author.url, friend_status = 'friend').exist():
                friendrequests = FriendRequest.objects.filter(url = current_author.url, friend_status = 'friend')
                for friendrequest in friendrequests:
                    friend = friendrequest.friend_with
                    if friend.host == request.get_host():
                        local_friends.append(friend)

            for local_friend in local_friends:
                if Post.objects.filter(author = local_friend).exist():
                    for post in Post.objects.filter(author = local_friend):
                        local_posts.append(post)

            #Get all posts private but visible to current user
            if Post.objects.filter(visibility='PRIVATE').exist():
                for post in Post.objects.filter(visibility = "PRIVATE").exist():
                    visible_to = change_visibleTo_to_list(post.visibleTo)
                    if current_author.url in visible_to:
                        local_posts.append(post)

            local_posts |= Post.objects.filter(visibility="SERVERONLY", unlisted=False)

            #Get all visible posts from remote server
            for node in ServerNode.objects.all():
                url = node.foreignHost + '/author/posts'
                header = {'X-Request-User-ID': current_author.host + '/author/' + str(current_author.id)}
                host = node.HostName
                authentication = HTTPBasicAuth(node.remoteUsername, node.remotePassword)
                try:
                    res = requests.get(url, auth=authentication, headers=header) #tell server current user url
                except:
                    return Response('cannot get posts from other server', status=status.HTTP_403_FORBIDDEN)
                # make sure json dumps
                res = res.json()

                remote_posts |= res['posts']

        #Convert local posts to json format
        posts = remote_posts
        try:
            local_posts = serializers.serialize('json', local_posts)
        except Exception:
            print("Unable to convert model objects to json")


        posts = remote_posts | local_posts

        #TODO
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)

class public_post(APIView):
    def get(self, request, format=None):
        posts = Post.objects.filter(visibility='PUBLIC', unlisted=False)
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)

class upload_post(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'addpost.html'
    def get(self, request, **kwargs):
        try:
            #print(user_id)
            current_user_profile = request.user.author
        except:
            return HttpResponse(status=404)
        new_post = Post.objects.create(author=current_user_profile)
        new_post.origin = "http://natto.herokuapp.com/posts/"+str(new_post.id)
        new_post.source = "http://natto.herokuapp.com/posts/"+str(new_post.id)
        new_post.save()
        serializer = PostSerializer(new_post)
        request.session["new_post_id"] = str(new_post.id)
        return Response({"serializer": serializer})

    def post(self, request, **kwargs):
        #try:
            #print("not here")
            #author = get_object_or_404(Author.objects.get(id=userid))
            #if author == current_user_profile:
        #print("aaaaaaaa"+str(preserve_id))
        try:
            #id = request.session["new_post_id"]
            id = uuid.UUID(request.session['new_post_id']).hex
            new_post = Post.objects.get(id=id)
            if not new_post:
                new_post = Post.objects.create(author=request.user.author)
        except:
            new_post = Post.objects.create(author=request.user.author)
        serializer = PostSerializer(new_post, data = request.data)
        if serializer.is_valid():
            print("what's the matter")
            serializer.save()
            # return Response({'serializer':serializer, 'profile': current_user_profile})
            return redirect("get_one_post", new_post.id)
        return JsonResponse({'serializer': serializer.data})

class my_post(APIView):
    def get(self, request, format=None):
        try:
            #print(user_id)
            current_user_profile = request.user.author
            if not current_user_profile:
                return HttpResponse(status=404)
        except:
            return HttpResponse(status=404)
        posts = Post.objects.filter(author=current_user_profile)
        pg_obj=PaginationModel()
        pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
        res=PostSerializer(instance=pg_res, many=True)
        print("Get My Post!!!!!!!!!!!!!")
        return pg_obj.get_paginated_response(res.data)

def del_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect("my_posts")

class edit_post(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'addpost.html'
    def get(self, request, post_id, **kwargs):
        try:
            #print(user_id)
            current_user_profile = request.user.author
            post = get_object_or_404(Post, pk=post_id)
        except:
            return HttpResponse(status=404)
        serializer = PostSerializer(post)
        return Response({"serializer": serializer})

    def post(self, request, post_id, **kwargs):
        #try:
            #print("not here")
            #author = get_object_or_404(Author.objects.get(id=userid))
            #if author == current_user_profile:
        #print("aaaaaaaa"+str(preserve_id))
        try:
            #id = request.session["new_post_id"]
            post = get_object_or_404(Post, pk=post_id)
        except:
            return HttpResponse(status=404)
        serializer = PostSerializer(post, data = request.data)
        if serializer.is_valid():
            print("what's the matter")
            serializer.save()
            # return Response({'serializer':serializer, 'profile': current_user_profile})
            return redirect("get_one_post", post.id)
        print(serializer.errors)
        print(serializer.data["contentType"])
        return JsonResponse({'serializer': serializer.data})

# http://service/posts/{POST_ID} access to a single post with id = {POST_ID}
class get_one_post(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'onePost.html'
    def get(self, request, post_id, **kwargs):
        try:
            print("get here")
            post = get_object_or_404(Post, pk = post_id)
            if not request.user:
                if post.unlisted==True or post.contentType=='image/png;base64' or post.contentType=='image/png;base64':
                    return HttpResponse(status=404)
        except:
            return HttpResponse(status=404)
        serializer = PostSerializer(post)
        return Response({"serializer": serializer.data})




# author/{author_id}/posts
# all posts made by author_id visible to authenticated user
class posts_from_an_author(APIView):
    '''
    1. Handle Authentication
    '''
    check_authentication()
    def get(self, request, author_id):
        is_remote = check_if_request_is_remote(request)
        posts = []
        if is_remote:
            try:
                user_id = request.META.get('HTTP_X_REQUEST_USER_ID', '')
                current_author = Author.objects.get(pk = user_id)
            except:
                return Response('remote user uuid not found', status=404)

        try:
            author = Author.objects.get(pk = author_id)
        except:
            return Response("author not found",status=404)

        if not is_remote:
            current_author = request.user.author

        if current_author == author:
            for post in Post.objects.filter(author = current_author):
                posts.append(post)
        else:
            '''public, friend, foaf, visible_to'''
            for post in Post.objects.filter(visibility='PUBLIC'):
                posts.append(post)

            author_url = author.url
            if FriendRequest.objects.filter(url = author_url, friend_with = current_author, friend_status = 'friend').exist():
                for post in Post.objects.filter(author = author, visibility='FRIENDS'):
                    posts.append(post)

            for post in Post.objects.filter(author = author, visibility='PRIVATE'):
                if current_author.id in post.visibleTo:
                    if post not in posts:
                        posts.append(post)

            #get post foaf, only local foaf
            friendrequests = []
            friend_objs = []
            if FriendRequest.objects.filter(url=author_url, friend_status='friend').exist():
                for friendrequest in FriendRequest.objects.filter(url = author_url, friend_status = 'friend'):
                    friendrequests.append(friendrequest)
                    friend_objs.append(friendrequest.friend_with)
                for friend in friend_objs:
                    friend_url = friend.url
                    if FriendRequest.objects.filter(url = friend_url, friend_with = current_author, friend_status = 'friend').exist():
                        for post in Post.objects.filter(author = author, visibility='FOAF'):
                            if post not in posts:
                                posts.append(post)

        posts = posts.order_by(F("published").desc())

        response_body = {}
        response_body['query'] = 'posts'
        response_body['count'] = str(len(posts))
        response_body['previous'] = current_author.host + "/author/posts?page=1"
        response_body['next'] = current_author.host + "/author/posts?page=2"

        response_body['posts'] = []
        for post in posts:
            serializer = PostSerializer(post).data
            serializer['postid'] = str(serializer['postid'])
            response_body['posts'].append(serializer)

        return Response(json.dumps(response_body), status=status.HTTP_200_OK)






