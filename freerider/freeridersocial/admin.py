from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Images)
admin.site.register(Comment)
admin.site.register(FriendRequest)
admin.site.register(ServerNode)

