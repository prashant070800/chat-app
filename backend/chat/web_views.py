from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from .models import Friendship, Message

User = get_user_model()

@login_required
def friends_list_view(request):
    user = request.user
    
    # Friends
    friendships = Friendship.objects.filter(
        (Q(sender=user) | Q(receiver=user)) & Q(status=Friendship.ACCEPTED)
    )
    friends = []
    for f in friendships:
        if f.sender == user:
            friends.append(f.receiver)
        else:
            friends.append(f.sender)
            
    # Pending Requests (Received)
    pending_requests = Friendship.objects.filter(receiver=user, status=Friendship.PENDING)
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests
    }
    return render(request, 'chat/friends.html', context)

@login_required
def search_users_view(request):
    query = request.GET.get('q')
    users = []
    if query:
        users = User.objects.filter(
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
        
    context = {
        'users': users,
        'query': query
    }
    return render(request, 'chat/search.html', context)

@login_required
def send_invite_view(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    sender = request.user
    
    if Friendship.objects.filter(sender=sender, receiver=receiver).exists() or \
       Friendship.objects.filter(sender=receiver, receiver=sender).exists():
        messages.warning(request, f"Friendship request already exists with {receiver.email}.")
    else:
        Friendship.objects.create(sender=sender, receiver=receiver, status=Friendship.PENDING)
        messages.success(request, f"Friend request sent to {receiver.email}.")
        
    return redirect('chat-search')

@login_required
def handle_request_view(request, friendship_id, action):
    friendship = get_object_or_404(Friendship, id=friendship_id, receiver=request.user)
    
    if action == 'accept':
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        messages.success(request, "Friend request accepted.")
    elif action == 'reject':
        friendship.status = Friendship.REJECTED
        friendship.save()
        messages.info(request, "Friend request rejected.")
        
    return redirect('chat-friends')

@login_required
def chat_room_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Mark messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    context = {
        'other_user': other_user,
    }
    return render(request, 'chat/chat_room.html', context)
