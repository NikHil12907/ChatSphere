from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True )
    is_private = models.BooleanField(default=False)
    active_users = models.ManyToManyField(User, related_name="active_rooms", blank=True)
    
    @staticmethod
    def get_or_create_private_room(user1, user2):
        usernames = sorted([user1.username, user2.username])
        room_name = f"private_{usernames[0]}_{usernames[1]}"
        room, created = Room.objects.get_or_create(name=room_name, is_private=True)
        if created:
            print(f"Room '{room_name}' created.")
        else:
            print(f"The Room is already exists.")
        return room
     
    def __str__(self) :
        return self.name
    
class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.timeStamp}"
    
    class Meta:
        ordering = ['timeStamp']
        
class PasswordResetOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'OTP for {self.user.username}' 
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    