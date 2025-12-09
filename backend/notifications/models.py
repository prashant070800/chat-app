from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPES = (
        ('friend_request', 'Friend Request'),
        ('message', 'New Message'),
        ('general', 'General'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPES, default='general')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.recipient}: {self.content}"
