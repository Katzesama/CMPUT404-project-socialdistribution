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
    print('in visible_post')

    def get(self, request, format=None):
        #print(request.get_host())
        check_authentication()
        print('pass authentication')
        is_remote = check_if_request_is_remote(request)

        local_posts = []
        remote_posts = []
        print(request.user.author.displayName)
        # if is_remote:
        #     try:
        #         #print(request)
        #         user_id = request.META.get('HTTP_X_REQUEST_USER_ID')
        #         print(user_id)
        #         current_author = Author.objects.get(pk=user_id)
        #         #print(current_author.displayName)
        #     except:
        #         return Response('remote user uuid not found', status=404)
        '''如果是local的request 优先向所有server发request'''
        if not is_remote:
            print('local request')
            current_author = request.user.author
            for node in ServerNode.objects.all():
                username = node.username
                pwd = node.password
                url = node.HostName + '/author/posts'
                authentication = HTTPBasicAuth(username, pwd)
                header = {'X-Request-User-ID': current_author.url}
                resp = requests.get(url, auth=authentication, headers=header)
                data = resp.json()
                if resp.status_code != 200:
                    return Response('Fail to get posts from other server', status=400)
                else:
                    for post in data['posts']:
                        remote_posts.append(post)
            print('get remote posts')

        else:
            print('remote request')
            author_url = request.META.get('HTTP_X_REQUEST_USER_ID', '')
            print(str(author_url))  # None
            try:
                current_author = Author.objects.filter(url=author_url)[0]
            except:
                '''Send a request back to get requestor's profile and create author object'''
                print('not reach here')
                #GET http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e
                resp_remote = get_requestor_info_with_url(request, author_url)
                data = resp_remote.json()
                print(data)
                current_author = create_local_author(data)

                # print('here')
                # print(author_url)
                # current_author = Author.objects.filter(url = author_url)[0]
                # print('get current author')



        '''We get current_author, need to get local visible posts'''

        # Get all posts posted by current user
        if Post.objects.filter(author=current_author).exists():
            for post in Post.objects.filter(author=current_author):
                if not post in local_posts:
                    local_posts.append(post)
        print('get my posts')
        # Get all public posts in local server
        if Post.objects.filter(visibility='PUBLIC').exists():
            for post in Post.objects.filter(visibility="PUBLIC", unlisted=False):
                if not post in local_posts:
                    local_posts.append(post)

        print('get local public posts')
        local_friends = []

        if FriendRequest.objects.filter(url=current_author.url,
                                        friend_status='friend').exists() or FriendRequest.objects.filter(
            friend_with=current_author, friend_status='friend').exists():
            friendrequests_sender = FriendRequest.objects.filter(url=current_author.url, friend_status='friend')
            friendrequests_receiver = FriendRequest.objects.filter(friend_with=current_author, friend_status='friend')
            friendrequests = friendrequests_sender | friendrequests_receiver
            for friendrequest in friendrequests:
                friend = friendrequest.friend_with
                if friend.host == current_author.host:
                    if not post in local_posts:
                        local_friends.append(friend)

        for local_friend in local_friends:
            if Post.objects.filter(author=local_friend).exists():
                for post in Post.objects.filter(author=local_friend):
                    if not post in local_posts:
                        local_posts.append(post)

        print('get local friend posts')

        # Get all posts private but visible to current user
        if Post.objects.filter(visibility='PRIVATE').exists():
            for post in Post.objects.filter(visibility="PRIVATE"):
                print(post.visibleTo)
                visible_to = change_visibleTo_to_list(post.visibleTo)
                if current_author.displayName in visible_to:
                    if not post in local_posts:
                        local_posts.append(post)

        print('get private visible to me posts')
        posts = remote_posts

        print(remote_posts)
        print(local_posts)
        for post in local_posts:
            serializer = PostSerializer(post).data
            serializer['id'] = str(serializer['id'])
            posts.append(serializer)

        # if not is_remote:
        #     print('in is_remote')
        #     data = resp.json()
        #     foreign_posts = data['posts']
        #     for f_p in foreign_posts:
        #         author_url = f_p['id']
        #         if not Author.objects.filter(url=author_url).exists():
        #             print(author_url)
        #             author_id = author_url.split('author/')[1]
        #             foreign_author = Author.objects.create(id=UUID(author_id), url=author_url,
        #                                                    displayName=f_p['displayName'], host=f_p['host'],
        #                                                    github=f_p['github'])
        if is_remote:
            print('its here')
            response = {}
            response['query'] = 'posts'
            response['count'] = len(posts)
            response['size'] = 50
            page = len(posts) // 50

            response['next'] = str(current_author.host + '/author/posts?page = ' + str(page + 1))
            response['last'] = str(current_author.host + '/author/posts?page = ' + str(page - 1))
            response['posts'] = posts

            print('return response')
            return Response(response, status=200)

        # TODO
        pg_obj = PaginationModel()
        pg_res = pg_obj.paginate_queryset(queryset=posts, request=request)
        res = PostSerializer(instance=pg_res, many=True)
        return pg_obj.get_paginated_response(res.data)
    # #author/posts/
    # def get(self, request, format=None):
    #     check_authentication()
    #     #print('im here')
    #     is_remote = check_if_request_is_remote(request)
    #
    #     print('is remote?'+ str(is_remote))
    #     local_posts = []
    #     remote_posts = []
    #     print('wtf')
    #     if is_remote:
    #         try:
    #             print('in is_remote')
    #             user_id = request.META.get('HTTP_X_REQUEST_USER_ID', '')
    #             #print(' user id '+ str(user_id))
    #             current_author = Author.objects.get(pk=user_id)
    #             #print(current_author.displayName)
    #         except:
    #             return Response('remote user uuid not found', status=404)
    #     if not is_remote:
    #         print('here')
    #         current_author = request.user.author
    #
    #         #Get all posts posted by current user
    #     if Post.objects.filter(author = current_author).exists():
    #         for post in Post.objects.filter(author=current_author):
    #             if not post in local_posts:
    #                 local_posts.append(post)
    #     print('look at here')
    #     #Get all public posts in local server
    #     if Post.objects.filter(visibility='PUBLIC').exists():
    #         for post in Post.objects.filter(visibility="PUBLIC", unlisted=False):
    #             if not post in local_posts:
    #                 local_posts.append(post)
    #     #Get all posts sent by local friend
    #     local_friends = []
    #
    #     if FriendRequest.objects.filter(url = current_author.url, friend_status = 'friend').exists() or FriendRequest.objects.filter(friend_with=current_author, friend_status = 'friend').exists():
    #         friendrequests_sender = FriendRequest.objects.filter(url = current_author.url, friend_status = 'friend')
    #         friendrequests_receiver = FriendRequest.objects.filter(friend_with = current_author, friend_status = 'friend')
    #         friendrequests = friendrequests_sender | friendrequests_receiver
    #         for friendrequest in friendrequests:
    #             friend = friendrequest.friend_with
    #             if friend.host == current_author.host:
    #                 if not post in local_posts:
    #                     local_friends.append(friend)
    #     #print('local friends' + str(local_friends))
    #
    #     for local_friend in local_friends:
    #         if Post.objects.filter(author = local_friend).exists():
    #             for post in Post.objects.filter(author = local_friend):
    #                 if not post in local_posts:
    #                     local_posts.append(post)
    #
    #     #Get all posts private but visible to current user
    #     if Post.objects.filter(visibility='PRIVATE').exists():
    #         for post in Post.objects.filter(visibility = "PRIVATE"):
    #             print(post.visibleTo)
    #             visible_to = change_visibleTo_to_list(post.visibleTo)
    #             if current_author.displayName in visible_to:
    #                 if not post in local_posts:
    #                     local_posts.append(post)
    #
    #     local_posts += Post.objects.filter(visibility="SERVERONLY", unlisted=False)
    #     print('request host name: '+request.get_host())
    #     #Get all visible posts from remote server
    #     #TODO if author object not stored locally store it
    #     for node in ServerNode.objects.all():
    #         print('node host name: '+node.HostName)
    #         url = node.HostName + '/author/posts/'
    #         header = {'X-Request-User-ID': current_author.host + '/author/' + str(current_author.id)}
    #         host = node.HostName
    #         authentication = HTTPBasicAuth(node.username, node.password)
    #         try:
    #             res = requests.get(url, auth=authentication, headers=header) #tell server current user url
    #             print(res)
    #         except:
    #             return Response('cannot get posts from other server', status=status.HTTP_403_FORBIDDEN)
    #         # make sure json dumps
    #
    #         remote_author = res['posts']['author'] #a dictionary
    #         author_id = remote_author['id']
    #         has_author_already = check_local_has_author(author_id)
    #         if not has_author_already:
    #             create_local_author(remote_author)
    #
    #
    #         res = res.json()
    #
    #         remote_posts += res['posts']
    #
    #     #Convert local posts to json format
    #     posts = remote_posts
    #     for post in local_posts:
    #         if post not in posts:
    #             posts.append(post)
    #     # posts = remote_posts + local_posts
    #
    #     #TODO
    #     pg_obj=PaginationModel()
    #     pg_res=pg_obj.paginate_queryset(queryset=posts, request=request)
    #     res=PostSerializer(instance=pg_res, many=True)
    #     return pg_obj.get_paginated_response(res.data)

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
            if FriendRequest.objects.filter(url=author_url, friend_status='friend').exists():
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






