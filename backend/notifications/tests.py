from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from chat.models import Friendship
from .models import Notification

User = get_user_model()

class NotificationTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(email='user_a@example.com', password='password123', first_name='User', last_name='A')
        self.user_b = User.objects.create_user(email='user_b@example.com', password='password123', first_name='User', last_name='B')
        
        self.client_a = APIClient()
        self.client_a.force_authenticate(user=self.user_a)
        
        self.client_b = APIClient()
        self.client_b.force_authenticate(user=self.user_b)

    def test_friend_request_notification(self):
        # User A sends friend request to User B
        Friendship.objects.create(sender=self.user_a, receiver=self.user_b, status=Friendship.PENDING)
        
        # Check if User B got a notification
        notifications = Notification.objects.filter(recipient=self.user_b)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().notification_type, 'friend_request')
        self.assertIn('sent you a friend request', notifications.first().content)

    def test_friend_accept_notification(self):
        # User A sends request
        friendship = Friendship.objects.create(sender=self.user_a, receiver=self.user_b, status=Friendship.PENDING)
        
        # User B accepts
        friendship.status = Friendship.ACCEPTED
        friendship.save()
        
        # Check if User A got a notification
        notifications = Notification.objects.filter(recipient=self.user_a)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().notification_type, 'friend_request')
        self.assertIn('accepted your friend request', notifications.first().content)

    def test_api_list_notifications(self):
        # Create a notification manually
        Notification.objects.create(recipient=self.user_a, content="Test Notification")
        
        response = self.client_a.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "Test Notification")

    def test_api_mark_read(self):
        notif = Notification.objects.create(recipient=self.user_a, content="Test Notification")
        
        response = self.client_a.post(f'/api/notifications/{notif.id}/mark_read/')
        self.assertEqual(response.status_code, 200)
        
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
