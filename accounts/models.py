from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Gaming preferences
    favorite_genres = models.ManyToManyField('games.Category', blank=True)
    gaming_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='beginner'
    )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar image
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_games_played = models.PositiveIntegerField(default=0)
    total_hours_played = models.PositiveIntegerField(default=0)
    achievements_count = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Friends Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"