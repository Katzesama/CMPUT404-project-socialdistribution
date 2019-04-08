import requests
from requests.auth import HTTPBasicAuth
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework.response import Response
from rest_framework import status
from uuid import UUID

#https://www.django-rest-framework.org/api-guide/authentication/
def check_authentication():
    print('check auth')
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

def check_if_request_is_remote(request):
    #print(request.user.node)
    if (ServerNode.objects.filter(auth_user = request.user).exists()):
        return True
    else:
        return False


def check_local_has_author(author_id):
    try:
        author = Author.objects.get(pk = author_id)
        return True
    except:
        return False

def create_local_author(data):
    host = data["host"]
    host = host.replace("localhost", "127.0.0.1")
    if not Author.objects.filter(id=UUID(data['id'].split('author/')[1])).exists():
        author = Author.objects.create(id=UUID(data['id'].split('author/')[1]), displayName=data["displayName"],
                                       url=data['url'], host=host)
        author.save()
    else:
        author = Author.objects.filter(id=UUID(data['id'].split('author/')[1]))[0]
    return author

def check_already_friends(sender_url, receiver_obj):

    if FriendRequest.objects.filter(url = sender_url, friend_with = receiver_obj, friend_status = 'friend').exists():
        return True
    else:
        return False

def reply_remote_friendrequest(data, node):
    url = node.HostName + '/friendrequest/'
    print('url:'+url)
    header = {"Content-Type": "application/json"}
    # sender = data['author']
    # data['author'] = data['friend']
    # data['friend'] = sender
    try:
        data = json.dumps(data)
    except: pass
    response = requests.post(url, headers=header, data=data, auth=HTTPBasicAuth(node.username,node.password))
    return response
    # if response.status_code == 200:
    #     return Response("friendrequest sent back", status=status.HTTP_200_OK)
    # else:
    #     return Response("friendrequest failed", status=response.status_code)

def calculate_page_for_post():
   # https: // stackoverflow.com / questions / 150505 / capturing - url - parameters - in -request - get
    return

def change_visibleTo_to_list(visibleTo):
    visibleTo = visibleTo.split(',')
    return visibleTo

def get_requestor_info_with_url(request, url):
    print(url)
    print(request)
    id = url.split('author/')[1]
    current_author_host = url.split('/author/')[0]
    if current_author_host == 'http://natto.herokuapp.com':
        current_author_host = request.scheme + '://myblog-6.heroku.com'

    request_url = current_author_host + '/author/' + id + '/api/'
        # print(request_url)
    print(request_url)
    node = ServerNode.objects.filter(HostName=current_author_host)[0]
    username = node.username
    pwd = node.password
        # print(username)
        # print(pwd)
    authentication = HTTPBasicAuth(username, pwd)
        # print('send request')
    resp = requests.get(request_url, auth=authentication)

    print(resp.content)

    return resp