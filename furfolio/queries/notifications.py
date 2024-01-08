from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from django.shortcuts import get_object_or_404
from . import chat as chat_queries
from .. import models


def create_message_notification(message: 'models.ChatMessage', recipient: 'models.User') -> 'models.ChatMessageNotification':
    notification = models.Notification.objects.create(
        recipient=recipient,
    )
    message_notification = models.ChatMessageNotification.objects.create(
        notification=notification,
        message=message,
    )
    return message_notification


def create_message_notifications_for_recipients(message: 'models.ChatMessage'):
    for recipient in chat_queries.get_recipients_of_message(message):
        create_message_notification(message, recipient)