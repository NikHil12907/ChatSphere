
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RoomForm, UserUpdateForm, ProfileUpdateForm
from .models import Room, Notification, Profile
from django.contrib import messages
# Create your views here.


def index(request):
    return render(request, 'chat/index.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            Profile.objects.get_or_create(user=user)
            return redirect('room_list')
        else:
            messages.error(request, 'Invalid Username and Password')
    return render(request, 'chat/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request,user)
                return redirect('login')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form':form})
        
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
        
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'chat/profile.html', context)

@login_required
def room_list(request):
    # rooms = Room.objects.all()
    users = User.objects.all()
    current_user = request.user
    recommended_users = users.exclude(id=current_user.id)
    rooms = Room.objects.exclude(name__startswith="private_").annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False, messages__user=request.user )
        )
    )   
    
    return render(request, 'chat/room_list.html', {'rooms' : rooms, 'users': users, 'recommended_users': recommended_users})

@login_required
def room(request, room_name):
    
    try:
        room = get_object_or_404(Room, name=room_name)
        messages = room.messages.order_by('-timeStamp')[:50]
        messages = messages[::-1]
    except Room.DoesNotExist:
        messages.error(request, "The Room you tried to access does not exists")
        return redirect('room_list')
    
    if room.is_private:
        other_user = room.active_users.exclude(id=request.user.id).first()
        display_picture = other_user.profile.profile_picture.url if other_user and hasattr(other_user, 'profile') else '/images/default-avatar.png'
    else:
        display_picture = '/images/group-icon.jpg'
    
    users = User.objects.all().exclude(id=request.user.id)
    rooms = Room.objects.all()
    Notification.objects.filter(user=request.user, room=room, is_read=False).update(is_read=True)
    return render(request, 'chat/room.html', {'room_name': room_name, 'rooms': rooms, 'username' : request.user.username, 'messages':messages, 'users':users, 'display_picture':display_picture})

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user
            room.save()
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'chat/create_room.html', {'form': form})

@login_required
def delete_room(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    
    if request.method == "POST":
        if request.user == room.creator:
            room.delete()
            messages.success(request, "Room Deleted Successfully")
        else:
            messages.error(request, "You are not authorized to delete this room")
        
    return redirect("room_list")   

@login_required
def search_user(request):
    query = request.GET.get('q','')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, 'chat/search_users.html', {'users':users, 'query':query})

@login_required
def private_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    if request.user == other_user:
        return redirect('room_list')
    
    room = Room.get_or_create_private_room(request.user, other_user)
    if not room:
        messages.error(request, "Could not create or find the private room.")
        return redirect('room_list')
    
    return render(request, "chat/private_chat.html", {'room_name':room.name, 'other_user':other_user, 'username':request.user.username})
