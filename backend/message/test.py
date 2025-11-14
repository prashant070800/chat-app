from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from backend.message.models import Room, RoomMember, RoomMemberStatus

User = get_user_model()


class RoomMemberTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="pass")
        self.user2 = User.objects.create_user(username="u2", password="pass")

        self.room = Room.objects.create(
            name="TestRoom",
            created_by=self.user1,
        )

    # ---------------------------------------------------------
    # ROOM TESTS
    # ---------------------------------------------------------
    def test_room_name_unique_per_user(self):
        with self.assertRaises(IntegrityError):
            Room.objects.create(
                name="TestRoom",
                created_by=self.user1,
            )

    # ---------------------------------------------------------
    # INVITATION TESTS
    # ---------------------------------------------------------
    def test_user_can_be_invited_once(self):
        RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        with self.assertRaises(IntegrityError):
            # Duplicate INVITED entry should raise due to UniqueConstraint
            RoomMember.objects.create(
                user=self.user2,
                room=self.room,
                status=RoomMemberStatus.INVITED,
            )

    def test_user_can_be_reinvited_after_rejected(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        rm.status = RoomMemberStatus.REJECTED
        rm.save()

        # Now reinvite (allowed)
        new_invite = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        self.assertEqual(new_invite.status, RoomMemberStatus.INVITED)

    def test_user_can_be_reinvited_after_removed(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        rm.status = RoomMemberStatus.ACCEPTED
        rm.save()

        rm.status = RoomMemberStatus.REMOVED
        rm.save()

        # Reinvite
        new_invite = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        self.assertEqual(new_invite.status, RoomMemberStatus.INVITED)

    # ---------------------------------------------------------
    # STATE TRANSITION RULES
    # ---------------------------------------------------------
    def test_invited_user_can_accept(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        rm.status = RoomMemberStatus.ACCEPTED
        rm.save()

        self.assertIsNotNone(rm.accepted_on)

    def test_invited_user_can_reject(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )

        rm.status = RoomMemberStatus.REJECTED
        rm.save()

        self.assertIsNotNone(rm.rejected_on)

    def test_accepted_user_can_be_removed(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
            status=RoomMemberStatus.ACCEPTED,
        )

        rm.status = RoomMemberStatus.REMOVED
        rm.save()

        self.assertIsNotNone(rm.removed_on)

    # ---------------------------------------------------------
    # INVALID TRANSITIONS
    # ---------------------------------------------------------
    def test_accepted_user_cannot_reject(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )
        rm.status = RoomMemberStatus.ACCEPTED
        rm.save()

        rm.status = RoomMemberStatus.REJECTED
        with self.assertRaises(ValidationError):
            rm.clean()

    def test_rejected_user_cannot_accept(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )
        rm.status = RoomMemberStatus.REJECTED
        rm.save()

        rm.status = RoomMemberStatus.ACCEPTED
        with self.assertRaises(ValidationError):
            rm.clean()

    def test_removed_user_cannot_accept(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
            status=RoomMemberStatus.ACCEPTED,
        )
        rm.status = RoomMemberStatus.REMOVED
        rm.save()

        rm.status = RoomMemberStatus.ACCEPTED
        with self.assertRaises(ValidationError):
            rm.clean()

    def test_only_invited_or_accepted_can_be_removed(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
            status=RoomMemberStatus.REJECTED,
        )

        rm.status = RoomMemberStatus.REMOVED
        with self.assertRaises(ValidationError):
            rm.clean()

    # ---------------------------------------------------------
    # TIMESTAMP TEST
    # ---------------------------------------------------------
    def test_timestamp_updates_on_status_change(self):
        rm = RoomMember.objects.create(
            user=self.user2,
            room=self.room,
        )
        old_invited_on = rm.invited_on

        # Accept
        rm.status = RoomMemberStatus.ACCEPTED
        rm.save()

        self.assertNotEqual(rm.accepted_on, None)
        self.assertEqual(rm.invited_on, old_invited_on)  # invited_on should not change

        # Remove
        rm.status = RoomMemberStatus.REMOVED
        rm.save()

        self.assertNotEqual(rm.removed_on, None)
