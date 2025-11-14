# class Message(models.Model):
from django.db import models
from django.forms import ValidationError
from django.utils import timezone

from backend.core.models import User

# Create your models here.


class CreatedModifiedBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Room(CreatedModifiedBaseModel):
    name = models.CharField(max_length=15, help_text="room name")

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="",
        related_name="rooms",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["created_by", "name"],
                name="unique_room_name_per_user",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.created_by})"


class RoomMemberStatus(models.TextChoices):
    INVITED = "INVITED", "Invited"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    REMOVED = "REMOVED", "Removed"


class RoomMember(CreatedModifiedBaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="room_memberships",
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="members",
    )

    status = models.CharField(
        max_length=12,
        choices=RoomMemberStatus.choices,
        default=RoomMemberStatus.INVITED,
        help_text="Current membership state",
    )

    # Timestamp fields for state events
    invited_on = models.DateTimeField(default=timezone.now)
    accepted_on = models.DateTimeField(null=True, blank=True)
    rejected_on = models.DateTimeField(null=True, blank=True)
    removed_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # ❗ Prevent two active invitations or accepted statuses
            models.UniqueConstraint(
                fields=["room", "user", "status"],
                condition=models.Q(status__in=["INVITED", "ACCEPTED"]),
                name="unique_active_membership",
            )
        ]

    def clean(self):
        """Enforce state machine rules."""
        # Existing instance
        if self.pk:
            old = RoomMember.objects.get(pk=self.pk)

            # ❌ Accepted member cannot reject
            if (
                old.status == RoomMemberStatus.ACCEPTED
                and self.status == RoomMemberStatus.REJECTED
            ):
                raise ValidationError("Accepted member cannot reject the invitation.")

            # ❌ Accepted member cannot accept again
            if (
                old.status == RoomMemberStatus.ACCEPTED
                and self.status == RoomMemberStatus.ACCEPTED
            ):
                raise ValidationError("Already accepted.")

            # ❌ Rejected member cannot accept
            if (
                old.status == RoomMemberStatus.REJECTED
                and self.status == RoomMemberStatus.ACCEPTED
            ):
                raise ValidationError("Rejected member cannot accept.")

            # ❌ Removed member cannot accept
            if (
                old.status == RoomMemberStatus.REMOVED
                and self.status == RoomMemberStatus.ACCEPTED
            ):
                raise ValidationError("Removed member cannot accept.")

            # ❌ Only accepted member can be removed
            if self.status == RoomMemberStatus.REMOVED and old.status not in [
                RoomMemberStatus.ACCEPTED,
                RoomMemberStatus.INVITED,
            ]:
                raise ValidationError("Only accepted or invited users can be removed.")

    def save(self, *args, **kwargs):
        """Set timestamps automatically based on state change."""
        if not self.pk:
            # New record → invited
            self.invited_on = timezone.now()

        else:
            old = RoomMember.objects.get(pk=self.pk)

            if old.status != self.status:  # status changed
                if self.status == RoomMemberStatus.ACCEPTED:
                    self.accepted_on = timezone.now()

                elif self.status == RoomMemberStatus.REJECTED:
                    self.rejected_on = timezone.now()

                elif self.status == RoomMemberStatus.REMOVED:
                    self.removed_on = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} → {self.room} ({self.status})"
