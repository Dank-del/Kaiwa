import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from.models import DirectMessage, Message, Room, RoomMembership
from django.core.exceptions import PermissionDenied

class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_room_messages(self, room_name):
        try:
            room = Room.objects.get(id=room_name)
            # Fetch messages sorted by timestamp and limit the query to the last 50 messages
            messages = Message.objects.filter(room=room).order_by("-timestamp")[:50]
            return [
                {
                    "id": message.id,
                    "content": message.content,
                    "username": message.user.username,
                    "user_id": message.user.id,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for message in messages
            ][::-1]
        except Room.DoesNotExist:
            return []

    @database_sync_to_async
    def has_access_to_room(self, room_name):
        try:
            room = Room.objects.get(id=room_name)
            RoomMembership.objects.get(user=self.user, room=room)
            return True
        except Room.DoesNotExist:
            return False
        except RoomMembership.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message, user):
        room = Room.objects.get(id=self.room_name)
        Message.objects.create(user=user, room=room, content=message)

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            raise PermissionDenied("You must be logged in to access this room.")

        room_name = self.scope["url_route"]["kwargs"]["room_name"]
        if not await self.has_access_to_room(room_name):
            raise PermissionDenied("You do not have access to this room.")

        self.room_name = room_name
        self.room_group_name = f"chat_{room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send historical messages after joining
        messages = await self.get_room_messages(room_name)
        for message in messages:
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message["content"],
                        "sender": {
                            "id": message["user_id"],
                            "username": message["username"],
                        },
                    }
                )
            )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Save message to database
        await self.save_message(message, self.user)
        if 'dm' in self.scope['url_route']['kwargs']:
            dm_id = self.scope['url_route']['kwargs']['dm_id']
            direct_message = DirectMessage.objects.get(id=dm_id)
            if direct_message.sender == self.scope['user'] or direct_message.receiver == self.scope['user']:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message
                    }
                )
        else:
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", "message": message}
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "sender": {"id": self.user.id, "username": self.user.username}}))
