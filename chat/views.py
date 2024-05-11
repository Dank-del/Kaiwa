from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.db.models import Q
from chat.forms import DirectMessageForm, RoomForm
from.models import DirectMessage, Room, RoomAdmin, RoomMembership, InviteLink
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

@login_required
def start_direct_message(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)
    if receiver!= request.user:
        DirectMessage.objects.create(sender=request.user, receiver=receiver)
        return render(request, 'direct_message.html', {'receiver': receiver})
    return render(request, 'error.html', {'message': 'Cannot start a direct message with yourself'})

@login_required
def exchange_message(request, dm_id):
    direct_message = get_object_or_404(DirectMessage, pk=dm_id)
    if request.method == 'POST':
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['content']
            direct_message.content = message
            direct_message.save()
            return render(request, 'direct_message.html', {'direct_message': direct_message})
    else:
        form = DirectMessageForm()
    return render(request, 'exchange_message.html', {'form': form, 'direct_message': direct_message})

@login_required
def manage_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    admins = RoomAdmin.objects.filter(room=room, is_admin=True)
    if request.user not in [admin.user for admin in admins]:
        return render(
            request,
            "error.html",
            {"message": "You do not have permission to manage this room"},
        )
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            RoomMembership.objects.create(user=user, room=room)
            return JsonResponse({'status': 'success'})
        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            membership = RoomMembership.objects.get(user=user, room=room)
            membership.delete()
            return JsonResponse({'status': 'success'})
        elif action == 'edit_title':
            title = request.POST.get('title')
            room.title = title
            room.save()
            return JsonResponse({'status': 'success'})
        elif action == 'create_invite_link':
            link = uuid.uuid4()
            InviteLink.objects.create(room=room, link=link, expires_at=timezone.now() + timedelta(days=7))
            return JsonResponse({"status": "success"})
    return render(request, 'chat/room/manage.html', {'room': room})

@login_required
def user_rooms(request):
    rooms = Room.objects.filter(users__in=[request.user])
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=True)
            RoomAdmin.objects.create(user=request.user, room=room, is_admin=True)
            RoomMembership.objects.create(user=request.user, room=room)
            return redirect('chats')
    else:
        form = RoomForm()
    return render(request, 'chat/room/user_rooms.html', {'rooms': rooms, 'form': form})

@login_required
def user_dms(request):
    dms = DirectMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    return render(request, 'chat/room/user_dms.html', {'dms': dms})

def index(request):
    return render(request, "chat/index.html")


@login_required
def room(request, room_name):
    room = Room.objects.get(id=room_name)
    # print(vars(room))
    return render(
        request,
        "chat/room.html",
        {"room_name": room_name, "room": room, "user": request.user},
    )

def home(request):
    return render(request, 'chat/home.html')

def search(request):
    return render(request, 'chat/search.html')

def share(request):
    return render(request, 'chat/share.html')

def chat(request):
    return render(request, 'chat/chat.html')