from django.contrib import admin
from chat.models import DirectMessage, Room, RoomAdmin, RoomMembership, InviteLink

# Register your models here.
admin.register(
    [DirectMessage, Room, RoomAdmin, RoomMembership, InviteLink]
)
