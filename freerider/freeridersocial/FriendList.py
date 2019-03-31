from .models import Author, FriendRequest
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from .serializer import AuthorSerializer
<<<<<<< HEAD
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
=======
from django.http import HttpResponse, JsonResponse
>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
from .serializer import FriendSerializer
from django.shortcuts import render, redirect
from collections import OrderedDict
from rest_framework import status
import requests, json
<<<<<<< HEAD
from django.urls import reverse


class FriendList(APIView):
    '''不知道行不行，如何让前端get到friends'''
    def get(self, request):
        current_user = request.user.author

        friends = FriendRequest.objects.filter(url = current_user.url, friend_status = 'friend')
        serializer = FriendSerializer(friends, many=True)
        return Response({'serializer': serializer.data})
=======

class FriendList(APIView):
    '''get friend of mine, for all friend request send a request to check their status'''
    def get(self, request):
        current_user = request.user.author

        friendrequests = FriendRequest.objects.filter(url = current_user.url)
        friendlist = list()
        #for friendrequest in friendrequests:
            # GET http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013/friends/127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
            # url_content = friendrequest.host + '/author/' #http://service/author
            # friend_obj = friendrequest.friend_with
            # if not str(friend_obj.host).endwith('/'):
            #     friend_host = friend_obj.host + '/'
            # friend_id = friend_obj.url.replace(str(friend_host),"") #get id out
            #
            # url = current_user.url
            # try:
            #     url = url.replace('https://', "")
            # except:
            #     url = url.replace('http://', '')
            #
            # url_content += '/' + str(friend_id) + '/friends/' + url
            # if not url_content.endwith('/'):
            #     url_content += '/'
            #
            # resp = requests.get(url_content, headers={'Content-Type': 'application/json'})
            # if json.loads(resp.content).get('friends'):
            #     friendlist.append(friend_obj)
            #
            #     friendrequest.friend_status = 'friend'
            #     friendrequest.save()
        for friend in friendrequests:
            author_id = current_user.id  # de305d54-75b4-431b-adb2-eb6b9e546013
            friend_url = friend.url  # 127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
            friend_id = friend_url.replace(friend.host, "")
            friend_host = friend.host
            url = current_user.url
            try:
                url = url.replace('https://', "")
            except:
                url = url.replace('http://', '')
            url = url.replace(str(author_id), '')

            if not friend_host.endwith("/"):
                friend_host += '/'
            # ask other host if its local author has our local author as friend
            # GET http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013/friends/127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
            url_content = friend_host + 'author/' + friend_id + '/friends/' + url + '/author/' + str(author_id)
            if not url_content.endwith('/'):
                url_content += '/'
            resp = requests.get(url_content, headers={'Content-Type': 'application/json'})
            if json.loads(resp.content).get('friends'):
                friendlist.append(friend)
                friend.friend_status = "friend"
                friend.save()

        return render(request, "DisplayFriends.html",{'author': current_user, 'friends': friendlist})
>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776


class DeleteFriend(APIView):
    def delete(self, request, friendid):
        try:
            friend = FriendRequest.objects.filter(pk = friendid)
        except:
            HttpResponse('friend not found', status=404)
        friend.delete()
<<<<<<< HEAD
        return HttpResponseRedirect(reverse('myfriends_render'))
=======
        return HttpResponse('friend is removed', status = 200)
>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776

# Ask if 2 authors are friends
# GET http://service/author/<authorid>/friends/<authorid2>
# STRIP the http:// and https:// from the URI in the restful query
# If you need a template (optional): GET http://service/author/<authorid1>/friends/<service2>/author/<authorid2>
# where authorid1 = de305d54-75b4-431b-adb2-eb6b9e546013 (actually author http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013 )
# where authorid2 =
# GET http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013/friends/127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
# Please escape / of IDs with %2F e.g. urllib.parse.quote( "http://service/author/whatever" , safe='~()*!.\'')
# responds with:
# {	"query":"friends",
#         # Array of Author UUIDs
#         "authors":[
#             "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
#             "http://127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891"
#         ],
#         # boolean true or false
#         "friends": true
# }
class CheckIfFriend(APIView):
    '''get a request asking if author1 and author2 is friend, author1 is local and author2 is remote'''
    def get(self, request, authorid1, service2, authorid2):
<<<<<<< HEAD
        is_friend = False
        try:
            author1 = Author.objects.filter(id = authorid1)
        except:
            pass
        try:
            author2 = Author.objects.filter(id = authorid2)
        except:
            pass

        if author1 and author2:
            friendrequest1 = FriendRequest.objects.filter(url = author1.url, friend_with = author2, friend_status = 'friend')
            friendrequest2 = FriendRequest.objects.filter(url = author2.url, friend_with = author1, friend_status = 'friend')
            if friendrequest1 or friendrequest2:
                is_friend = True

            authors = []
            authors.append(author1.url)
            authors.append(author2.url)
            response_body = {
                "query": "friends",
                "authors": authors,
                "friends": is_friend,
            }

        else:
            return Response("Users not defined", status=404)
        return Response(response_body, status=status.HTTP_200_OK)
=======
        author1 = get_object_or_404(Author, id = authorid1)
        author2_url = service2 + '/'+authorid2
        '''Check if author1 follows author2 = Check if local host stores author2'''
        try:
            friend = Author.objects.filter(url = author2_url)
        except:
            authors = list()
            authors.append(author1.url)
            authors.append(author2_url)
            response = OrderedDict([
                ("query", "friends"),
                ("authors", authors),
                ("friends", False),
            ])

        try:
            #Check if author1 follows author2
            checkfriend = FriendRequest.objects.filter(url = author1.url, friend_with = friend, friend_status = 'friend')
        except:
            authors = list()
            authors.append(author1.url)
            authors.append(author2_url)
            response = OrderedDict([
                ("query", "friends"),
                ("authors", authors),
                ("friends", False),
            ])

        if checkfriend:
            authors = list()
            authors.append(author1.url)
            authors.append(author2_url)
            response = OrderedDict([
                ("query", "friends"),
                ("authors", authors),
                ("friends", True),
            ])

        else:
            return Response("Impossible", status=404)
        return Response(response, status=status.HTTP_200_OK)
>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776

# ask a service GET http://service/author/<authorid>/friends/
# responds with:
# {
# 	"query":"friends",
# 	# Array of Author UUIDs
# 	"authors":[
# 		"http://host3/author/de305d54-75b4-431b-adb2-eb6b9e546013",
# 		"http://host2/author/ae345d54-75b4-431b-adb2-fb6b9e547891"
# 	]
# }
class FriendsOfAuthor(APIView):
    '''get friendquery of an author given his author url'''
    def get(self, request, authorid):
        author = get_object_or_404(Author, pk = authorid)
<<<<<<< HEAD
        friendlist = list()

        friends = FriendRequest.objects.filter(url = author.url, friend_status = 'friend')
        for friend in friends:
            friend_obj = friend.friend_with
            friend_url = friend_obj.url
            friendlist.append(friend_url)

        response_body = {
            "query": "friends",
            "authors": friendlist,
        }
        return Response(response_body, status=status.HTTP_200_OK)

    # ask a service if anyone in the list is a friend
    # POST to http://service/author/<authorid>/friends
=======
        friends = FriendRequest.objects.filter(url = author.url)
        friendlist = list()
        for friend in friends:
            author_id = author.id #de305d54-75b4-431b-adb2-eb6b9e546013
            friend_url = friend.url #127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
            friend_id = friend_url.replace(friend.host, "")
            friend_host = friend.host
            url = author.url
            try:
                url = url.replace('https://', "")
            except:
                url = url.replace('http://','')
            url = url.replace(str(author_id),'')

            if not friend_host.endwith("/"):
                friend_host += '/'
            #ask other host if its local author has our local author as friend
            # GET http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013/friends/127.0.0.1%3A5454%2Fauthor%2Fae345d54-75b4-431b-adb2-fb6b9e547891
            url_content = friend_host + 'author/' + friend_id + '/friends/' + url + '/author/' + str(author_id)
            if not url_content.endwith('/'):
                url_content += '/'
            resp = requests.get(url_content, headers={'Content-Type': 'application/json'})
            if json.loads(resp.content).get('friends'):
                friendlist.append(friend)
                friend.friend_status = "friend"
                friend.save()

        response = OrderedDict([
            ('query', friends),
            ('authors', friendlist),
        ])
        return Response(response, status=status.HTTP_200_OK)


>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776
    def post(self, request, authorid):
        data = request.data
        try:
            author = get_object_or_404(Author, authorid)
            data = request.data
            if data['query'] == 'friends':
<<<<<<< HEAD
                friends_list = FriendRequest.objects.filter(url = author.url, friend_status = 'friend')
=======
                friends_list = FriendRequest.objects.filter(url = author.url)
>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776
                authors = data['authors']
                confirm_friends = []
                for author_url in authors:
                    for friend_obj in friends_list:
<<<<<<< HEAD
                        friend_id = str(friend_obj.url)
                        if friend_id in author_url:
=======
                        firend_id = str(friend_obj.id)
                        if firend_id in author_url:
>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776
                            confirm_friends.append(author_url)
                responsBody = {
                    "query": "friends",
                    "author": author.url,
                    "authors": confirm_friends,
                }
                return Response(json.dumps(responsBody), status=200)
            else:
                return Response("Wrong query format", status=400)
        except:
            return Response("Author doesn't exist", status=404)
<<<<<<< HEAD
=======


>>>>>>> 9f8e8720405a02b200c2b12d4d8e5b4ccd1c7776
