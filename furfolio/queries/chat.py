from typing import Union
from django.shortcuts import get_object_or_404
from django.db.models import Manager
from django.db.models import Q


from .. import models


def create_chat_for_commission(commission: 'models.Commission'):
    commission_chat = models.CommissionChat.objects.create(
        commission=commission,
    )
    # add participants
    commissioner = commission.commissioner
    commissionee = commission.offer.author
    for user in [commissioner, commissionee]:
        models.ChatParticipant.objects.create(
            chat=commission_chat,
            participant=user,
        )


def get_messages_from_chat(
        chat: 'models.Chat') -> 'Manager[models.ChatMessage]':
    return models.ChatMessage.objects.filter(chat=chat)


def get_chat_by_pk(pk) -> 'models.Chat':
    return get_object_or_404(models.Chat, pk=pk)


def get_commission_chat_by_commission(commission: 'models.Commission') -> Union['models.CommissionChat', None]:
    try:
        return models.CommissionChat.objects.get(
            commission=commission,
        )
    except models.CommissionChat.DoesNotExist:
        return None


def test_user_is_participant_of_chat(
        chat: 'models.Chat',
        user: 'models.User') -> bool:
    return models.Chat.objects.filter(
        pk=chat.pk,
        chatparticipant__participant=user,
    ).exists()


def get_recipients_of_message(
        message: 'models.ChatMessage') -> 'Manager[models.User]':
    # the message author is never a "recipient" of their own message
    return models.User.objects.filter(
        chatparticipant__chat=message.chat
    ).exclude(
        pk=message.author.pk
    )
