from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Friendship

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

class FriendshipSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Friendship
        fields = ('id', 'sender', 'receiver', 'receiver_email', 'status', 'created_at')
        read_only_fields = ('sender', 'receiver', 'status', 'created_at')

    def create(self, validated_data):
        receiver_email = validated_data.pop('receiver_email').lower()
        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        sender = self.context['request'].user
        if sender == receiver:
            raise serializers.ValidationError("You cannot invite yourself.")
        
        if Friendship.objects.filter(sender=sender, receiver=receiver).exists() or \
           Friendship.objects.filter(sender=receiver, receiver=sender).exists():
            raise serializers.ValidationError("Friendship request already exists.")

        friendship = Friendship.objects.create(sender=sender, receiver=receiver, status=Friendship.PENDING)
        return friendship
