from django.contrib import admin
from .models import Room, Message, Profile, File, PrivateMessage

# Register your models here.
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Profile)
admin.site.register(File)
admin.site.register(PrivateMessage)
