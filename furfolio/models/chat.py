from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timesince
import math

from .. import validators as furfolio_validators
from .commissions import Commission
from .support import SupportTicket
from ..queries import chat as chat_queries
from ..queries import notifications as notification_queries


class Chat(models.Model):
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return self.get_name()

    def get_name(self):
        # for each possible child model of Chat, try to get the name
        try:
            return self.commissionchat.get_name()
        except CommissionChat.DoesNotExist:
            pass

        try:
            return self.supportticketchat.get_name()
        except SupportTicketChat.DoesNotExist:
            pass

        return "Generic Chat"

    def get_participants(self):
        return chat_queries.get_chat_participants(self)


class CommissionChat(Chat):
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
    )

    def get_name(self):
        return f"{self.commission.offer.name}"


class SupportTicketChat(Chat):
    support_ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
    )

    def get_name(self):
        return f"{self.support_ticket.title}"


class ChatParticipant(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return f"\"{self.participant}\" in chat \"{self.chat}\""


class ChatMessage(models.Model):

    MESSAGE_MAX_LENGTH = math.ceil(
        settings.AVERAGE_CHARACTERS_PER_WORD * 350)

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    message = models.TextField(
        name="message",
        max_length=MESSAGE_MAX_LENGTH,
    )
    attachment = models.FileField(
        name="attachment",
        blank=True,
        validators=[
            furfolio_validators.validate_commission_message_attachment_has_max_size,
        ]
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return f"\"{self.author}\" made message in \"{self.chat}\""

    def timesince_created(self):
        return timesince.timesince(self.created_date)

    def get_html_id(self) -> str:
        return "message_" + str(self.pk)

    def get_absolute_url(self):
        return reverse("chat", kwargs={
                       "pk": self.chat.pk}) + "#" + self.get_html_id()

    def clean(self) -> None:
        furfolio_validators.validate_chat_message_author_is_participant(self)
        return super().clean()

    def save(self, *args, **kwargs):
        # if message is new, notify all recipients
        if not self.pk:
            save_return = super().save(*args, **kwargs)
            notification_queries.create_message_notifications_for_recipients(
                self)
            return save_return
        else:
            return super().save(*args, **kwargs)
