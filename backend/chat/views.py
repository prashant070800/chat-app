from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Friendship
from .serializers import FriendshipSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class FriendshipViewSet(viewsets.ModelViewSet):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(Q(sender=user) | Q(receiver=user))

    @decorators.action(detail=False, methods=['post'])
    def send_invite(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=['post'])
    def accept_invite(self, request, pk=None):
        friendship = self.get_object()
        if friendship.receiver != request.user:
            return Response({"detail": "You can only accept requests sent to you."}, status=status.HTTP_403_FORBIDDEN)
        
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        return Response({"detail": "Friend request accepted."}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['post'])
    def reject_invite(self, request, pk=None):
        friendship = self.get_object()
        if friendship.receiver != request.user:
            return Response({"detail": "You can only reject requests sent to you."}, status=status.HTTP_403_FORBIDDEN)
        
        friendship.status = Friendship.REJECTED
        friendship.save()
        return Response({"detail": "Friend request rejected."}, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=['get'])
    def list_friends(self, request):
        user = request.user
        friendships = Friendship.objects.filter(
            (Q(sender=user) | Q(receiver=user)) & Q(status=Friendship.ACCEPTED)
        )
        friends = []
        for f in friendships:
            if f.sender == user:
                friends.append(f.receiver)
            else:
                friends.append(f.sender)
        
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['get'])
    def list_pending_requests(self, request):
        user = request.user
        # Requests received by me that are pending
        friendships = Friendship.objects.filter(receiver=user, status=Friendship.PENDING)
        serializer = self.get_serializer(friendships, many=True)
        return Response(serializer.data)
