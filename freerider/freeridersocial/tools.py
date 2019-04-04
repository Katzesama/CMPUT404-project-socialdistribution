import requests
from requests.auth import HTTPBasicAuth
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework.response import Response
from rest_framework import status

#https://www.django-rest-framework.org/api-guide/authentication/
def check_authentication():
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

def check_if_request_is_remote(request):
    #print(request.user.node)
    print(request.user.author.host)
    if (ServerNode.objects.filter(auth_user = request.user).exists()):
        #print(request.user.author.host)
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
    author = Author.objects.create(id=data['id'], displayName=data["displayName"], url = data['url'], host=host)
    author.save()

def check_already_friends(sender_url, receiver_obj):

    if FriendRequest.objects.filter(url = sender_url, friend_with = receiver_obj, friend_status = 'friend').exist():
        return True
    else:
        return False

def reply_remote_friendrequest(data, node):
    url = node.HostName
    header = {"Content-Type": "application/json"}
    sender = data['author']
    data['author'] = data['friend']
    data['friend'] = sender
    try:
        data = json.dumps(data)
    except: pass
    response = requests.post(url, headers=header, data=data, auth=HTTPBasicAuth(node.username,node.remotePassword))
    if response.status_code == 200:
        return Response("friendrequest sent back", status=status.HTTP_200_OK)
    else:
        return Response("friendrequest failed", status=response.status_code)

def calculate_page_for_post():
   # https: // stackoverflow.com / questions / 150505 / capturing - url - parameters - in -request - get
    return

def change_visibleTo_to_list(visibleTo):
    visibleTo = visibleTo.split(',')
    return visibleTo
