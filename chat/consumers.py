import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room,Message,Notification
from asgiref.sync import async_to_sync
from django.utils.timezone import now

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = "chat_%s" % self.room_name
        self.room_group_name = f"chat_{self.room_name}"

        self.user = self.scope['user']
        try:
            room, created = await database_sync_to_async(Room.objects.get_or_create)(name=self.room_name)
        except ObjectDoesNotExist:
            await self.close()
            return

        if room.is_private:
            users = self.room_name.split('_')[1:]
            if self.user.username not in users:
                await self.close()
                return
            
        # Join The Room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_add(
            "notifications",
            self.channel_name
        )
        
        await self.accept()
        
        await self.mark_user_active_in_room(self.user, self.room_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_add(
            "notifications",
            self.channel_name
        )
        
        await self.mark_user_inactive_in_room(self.user, self.room_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        timestamp = now().strftime("%H:%M")
        
        await self.save_message(self.user.username, message, self.room_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'username': self.user.username,
                'timestamp':timestamp
                
            }
        )
        
        await self.notify_out_of_room_users(self.room_name, self.user.username, message)

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message':message,
            'username': username,
            'timestamp': timestamp
            
        }))
        
    async def notify_users(self, event):
        await self.send(text_data=json.dumps({
            "type":"notify_users",
            "room_name":event["room_name"]
        }))

    @database_sync_to_async
    def save_message(self, username, message, room_name):
        room = Room.objects.get(name=room_name)
        user = User.objects.get(username=username)
        Message.objects.create(room=room, user=user, content=message)  
    
    @database_sync_to_async
    def mark_user_active_in_room(self, user, room_name):
        room = Room.objects.get(name=room_name)
        room.active_users.add(user)
        
    @database_sync_to_async
    def mark_user_inactive_in_room(self, user, room_name):
        room = Room.objects.get(name=room_name)
        room.active_users.remove(user)
        
    @database_sync_to_async
    def notify_out_of_room_users(self, room_name, sender_username, message):
        room = Room.objects.get(name=room_name)
        inactive_users = room.active_users.exclude(username=sender_username)
        
        for user in inactive_users:
            Notification.objects.create(
                user=user,
                room=room,
                sender=sender_username,
                message=message,
                is_read=False,
            )
        
        async_to_sync(self.channel_layer.group_send)(
            "notifications",{
                "type":"notify_users",
                "room_name":room_name,
            }
        )
        
                   
        
        
        