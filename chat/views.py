import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from chat.forms import DirectMessageForm, RoomForm
from .forms import UserProfileForm
from .models import DirectMessage, Room, RoomAdmin, RoomMembership, InviteLink


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
    if receiver != request.user:
        DirectMessage.objects.create(sender=request.user, receiver=receiver)
        return render(request, 'dm/direct_message.html', {'receiver': receiver})
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
            return render(request, 'dm/direct_message.html', {'direct_message': direct_message})
    else:
        form = DirectMessageForm()
    return render(request, 'dm/exchange_message.html', {'form': form, 'direct_message': direct_message})


@login_required
def manage_room(request, room_id):
    room_data = get_object_or_404(Room, pk=room_id)

    # Check if user is admin
    if not RoomAdmin.objects.filter(room=room_data, user=request.user, is_admin=True).exists():
        return render(request, "error.html",
                      {"message": "You do not have permission to manage this room"})

    members = RoomMembership.objects.filter(room=room_data)
    invite_links = InviteLink.objects.filter(room=room_data)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            RoomMembership.objects.get_or_create(user=user, room=room_data)

        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, pk=user_id)
            RoomMembership.objects.filter(user=user, room=room_data).delete()

        elif action == 'edit_title':
            title = request.POST.get('title')
            room_data.title = title
            room_data.save()

        elif action == 'create_invite_link':
            link = uuid.uuid4()
            InviteLink.objects.create(room=room_data, link=link, expires_at=timezone.now() + timedelta(days=7))

        elif action == 'delete_invite_link':
            link_id = request.POST.get('link_id')
            invite_link = get_object_or_404(InviteLink, id=link_id, room=room_data)
            invite_link.delete()

        # Refresh the queryset after modifications
        members = RoomMembership.objects.filter(room=room_data)
        invite_links = InviteLink.objects.filter(room=room_data)

    context = {
        'room': room_data,
        'members': members,
        'invite_links': invite_links,
    }

    return render(request, 'chat/room/manage.html', context)


@login_required
def user_rooms(request):
    rooms = Room.objects.filter(users__in=[request.user])
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room_data = form.save(commit=True)
            RoomAdmin.objects.create(user=request.user, room=room_data, is_admin=True)
            RoomMembership.objects.create(user=request.user, room=room_data)
            return redirect('chats')
    else:
        form = RoomForm()
    return render(request, 'chat/room/user_rooms.html', {'rooms': rooms, 'form': form})


@login_required
def user_dms(request):
    dms = DirectMessage.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    return render(request, 'chat/room/user_dms.html', {'dms': dms})


@login_required
def room(request, room_name):
    room_data = Room.objects.get(id=room_name)
    print(request.user.id)
    # print(vars(room))
    return render(
        request,
        "chat/room.html",
        {"room_name": room_name, "room": room_data, "user": request.user, "hide_bottom": True},
    )


def home(request):
    return render(request, 'chat/home.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            # Handle password change
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep the user logged in

            user.save()

            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'chat/profile.html', {'form': form})


def share(request):
    return render(request, 'chat/share.html')


def chat(request):
    return render(request, 'chat/chat.html')
