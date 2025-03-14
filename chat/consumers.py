import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room,Message,Notification,File, PrivateMessage
from asgiref.sync import async_to_sync
from django.utils.timezone import now

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(f"Connected to room: {self.room_name}")
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
        print(f"Recieved Data: {data}")
        print(f"Room_name :{self.room_name}")
        
        if 'message' in data:
            message = data['message']
            timestamp = now().strftime("%H:%M")
            
            await self.save_message(self.user.username, message, self.room_name)
            print(f"Sending Message: {message}")
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
        
        elif 'file' in data:
            try:    
                file_data = data['file']
                filename = data['filename']
                filetype = data['filetype']
            
                await self.save_file(self.user.username, file_data, filename, filetype, self.room_name)
            
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        'type':'chat_file',
                        'file': file_data,
                        'filename': filename,
                        'filetype': filetype,
                        'username': self.user.username,
                        'timestamp': now().strftime("%H:%M")
                    }
                )
            except KeyError as e:
                print(f"KeyError: {e} - Data Received: {data}")
            
    
    async def chat_file(self, event):
        file_data = event['file']
        filename = event['filename']
        filetype = event['filetype']
        # timestamp = event['timestamp']
        
        await self.send(text_data=json.dumps({
            'file': file_data,
            'filename': filename,
            'filetype': filetype,
            'username': self.user.username,
            # 'timestamp': timestamp
        }))        

    async def chat_message(self, event):
        print(f"Chat Message recived: {event}")
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
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
        try:
            if "private_" in room_name:
                users = room_name.split('_')[1:]
                sender = User.objects.get(username=username)
                receiver = User.objects.get(username=users[1] if users[0] == username else users[0])
                PrivateMessage.objects.create(sender=sender, receiver=receiver, content=message)
            else:
                room = Room.objects.get(name=room_name)
                print(f"Saving message to room: {room.name}")
                user = User.objects.get(username=username)
                Message.objects.create(room=room, user=user, content=message)  
        except Exception as e:
            print(f"Error saving message: {e}")
            
    
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
        
        try:
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
        except Room.DoesNotExist:
            print(f"Room {room_name} does not exist")
        except Exception as e:
            print(f"Error Notifying users: {str(e)}")
        
    @database_sync_to_async
    def save_file(self, username, file_data, filename, filetype, room_name):
        room = Room.objects.get(name=room_name)
        user = User.objects.get(username=username)
        
        File.objects.create(
            room=room,
            user=user,
            filename=filename,
            filetype=filetype,
            content=file_data
        )                  
        
        
        