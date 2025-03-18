from django import forms
from .models import Room, Profile
from django.contrib.auth.forms import User

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' : 'Enter Room Name',
                'autocomplete' : 'off', 
            })
        }
        
        

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'email']
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'dob']