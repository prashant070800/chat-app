from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from chat.models import Friendship, Message

User = get_user_model()

class ChatE2ETest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(email='user_a@example.com', password='password123', first_name='User', last_name='A')
        self.user_b = User.objects.create_user(email='user_b@example.com', password='password123', first_name='User', last_name='B')
        
        # Create friendship
        Friendship.objects.create(sender=self.user_a, receiver=self.user_b, status=Friendship.ACCEPTED)
        
        self.client_a = APIClient()
        self.client_a.force_authenticate(user=self.user_a)
        
        self.client_b = APIClient()
        self.client_b.force_authenticate(user=self.user_b)

    def test_chat_flow(self):
        # 1. User A sends message to User B
        response = self.client_a.post('/api/chat/messages/', {
            'receiver_id': self.user_b.id,
            'content': 'Hello User B'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        
        # 2. User B retrieves messages
        response = self.client_b.get(f'/api/chat/messages/?user_id={self.user_a.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Hello User B')
        self.assertEqual(response.data[0]['sender']['id'], self.user_a.id)
        
        # 3. User B replies to User A
        response = self.client_b.post('/api/chat/messages/', {
            'receiver_id': self.user_a.id,
            'content': 'Hi User A, nice to meet you'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        
        # 4. User A retrieves messages
        response = self.client_a.get(f'/api/chat/messages/?user_id={self.user_b.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[1]['content'], 'Hi User A, nice to meet you')
        self.assertEqual(response.data[1]['sender']['id'], self.user_b.id)
        
        # 5. Verify messages are ordered by timestamp
        self.assertTrue(response.data[0]['timestamp'] < response.data[1]['timestamp'])

    def test_chat_room_view(self):
        self.client.force_login(self.user_a)
        response = self.client.get(f'/chat/room/{self.user_b.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_room.html')
        self.assertContains(response, f'Chat with {self.user_b.first_name}')

    def test_friends_list_view(self):
        self.client.force_login(self.user_a)
        response = self.client.get('/chat/friends/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/friends.html')
        # Check if the Chat link is present and has the correct URL
        expected_url = f'/chat/room/{self.user_b.id}/'
        self.assertContains(response, f'href="{expected_url}"')

    def test_list_messages_with_cursor(self):
        # Create 3 messages
        Message.objects.create(sender=self.user_a, receiver=self.user_b, content="Msg 1")
        msg2 = Message.objects.create(sender=self.user_a, receiver=self.user_b, content="Msg 2")
        Message.objects.create(sender=self.user_a, receiver=self.user_b, content="Msg 3")
        
        # Fetch messages after msg2
        response = self.client_b.get(f'/api/chat/messages/?user_id={self.user_a.id}&after_id={msg2.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "Msg 3")
