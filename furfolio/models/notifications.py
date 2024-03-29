from django.db import models
from django.conf import settings
from django.urls import reverse
from .offers import Offer
from .chat import ChatMessage
from .commissions import Commission
from .support import SupportTicket
from .. import mixins

"""
When creating a notification sub-model,
add a receiver that deletes the parent model object
when its child is deleted.

Also add a test case to confirm the parent is deleted.
"""


class Notification(mixins.GetFullUrlMixin, models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    seen = models.BooleanField(
        default=False,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)

    def __str__(self):
        return f"\"{self.recipient}\" has a notification"

    def get_absolute_url(self):
        return reverse("open_notification", kwargs={"pk": self.pk})

    def get_content_url(self) -> str | None:
        """
        Returns the url that this notification points to.
        This url points to the content it is representing.
        This url does not "open" the notification.
        """
        if hasattr(self, "chatmessagenotification"):
            return self.chatmessagenotification.message.get_absolute_url()
        elif hasattr(self, "offerpostednotification"):
            return self.offerpostednotification.offer.get_absolute_url()
        elif hasattr(self, "commissionstatenotification"):
            return self.commissionstatenotification.commission.get_absolute_url()
        elif hasattr(self, "commissioncreatednotification"):
            return self.commissioncreatednotification.commission.get_absolute_url()
        elif hasattr(self, "userfollowednotification"):
            return self.userfollowednotification.follower.get_absolute_url()
        elif hasattr(self, "supportticketstatenotification"):
            return self.supportticketstatenotification.support_ticket.get_absolute_url()
        else:
            return None


class ChatMessageNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"\"{self.notification.recipient}\" has a chat message notification"


class OfferPostedNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"\"{self.notification.recipient}\" has been notified of a new offer \"{self.offer.name}\""


class CommissionStateNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
    )
    commission_state = models.CharField(
        name="state",
        max_length=11,
        choices=Commission.STATE_CHOICES,
    )

    def __str__(self):
        return f"commission of offer \"{self.commission.offer.name}\" has changed its state to {self.state}"


class CommissionCreatedNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"commission of offer \"{self.commission.offer.name}\" has been created"


class UserFollowedNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"user \"{self.follower.username}\" is following you \"{self.notification.recipient.username}\""


class SupportTicketStateNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    support_ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
    )
    support_ticket_state = models.CharField(
        max_length=13,
        choices=SupportTicket.STATE_CHOICES,
    )

    def __str__(self):
        return f"support ticket \"{self.support_ticket.title}\" has changed its state to {self.support_ticket_state}"
