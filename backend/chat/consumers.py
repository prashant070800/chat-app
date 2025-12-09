import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        
        if not self.user.is_authenticated:
            await self.close()
            return

        # Create a consistent room name for the two users
        users = sorted([int(self.user.id), int(self.other_user_id)])
        self.room_group_name = f"chat_{users[0]}_{users[1]}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        receiver_id = self.other_user_id

        # Save message to database
        saved_message = await self.save_message(self.user.id, receiver_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': saved_message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        return {
            'id': message.id,
            'content': message.content,
            'sender': {
                'id': sender.id,
                'first_name': sender.first_name,
                'last_name': sender.last_name,
                'email': sender.email
            },
            'timestamp': message.timestamp.isoformat()
        }
