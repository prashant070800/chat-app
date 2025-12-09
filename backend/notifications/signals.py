from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Friendship
from .models import Notification

@receiver(post_save, sender=Friendship)
def create_friendship_notification(sender, instance, created, **kwargs):
    if created:
        # New friend request
        Notification.objects.create(
            recipient=instance.receiver,
            notification_type='friend_request',
            content=f"{instance.sender.first_name} sent you a friend request."
        )
    elif instance.status == Friendship.ACCEPTED:
        # Friend request accepted
        # Notify the sender of the request that it was accepted
        # Avoid duplicate notifications if saved multiple times
        if not Notification.objects.filter(
            recipient=instance.sender,
            notification_type='friend_request',
            content__contains="accepted"
        ).exists():
             Notification.objects.create(
                recipient=instance.sender,
                notification_type='friend_request',
                content=f"{instance.receiver.first_name} accepted your friend request."
            )
