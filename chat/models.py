from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True )
    is_private = models.BooleanField(default=False)
    is_group = models.BooleanField(default=False)
    participant = models.ForeignKey(User, related_name='private_rooms', null=True, blank=True, on_delete=models.SET_NULL)
    active_users = models.ManyToManyField(User, related_name="active_rooms", blank=True)
    
    @staticmethod
    def get_or_create_private_room(user1, user2):
        usernames = sorted([user1.username, user2.username])
        room_name = f"private_{usernames[0]}_{usernames[1]}"
        room, created = Room.objects.get_or_create(name=room_name, is_private=True)
        if created:
            print(f"Room '{room_name}' created.")
            
            room.participant = user2 if room.creator == user1 else user1
            room.save()
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
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"
    
class Profile(models.Model):
    user =  models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='/images/default-avatar.png')
    dob = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
class File(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='files')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    content = models.FileField(upload_to='uploads/')
    filetype = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} uploaded by {self.user.username} in {self.room.name}"
    
class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Private from {self.sender.username} to {self.receiver.username} at {self.timestamp}" 