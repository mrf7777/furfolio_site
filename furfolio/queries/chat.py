from django.shortcuts import get_object_or_404
from django.db.models import Manager

from .. import models


def create_chat_for_commission(commission: 'models.Commission'):
    # create chat then create participants for
    # the commissioner and commissionee
    chat = models.Chat.objects.create(
        name=commission.offer.name,
    )
    commissioner = commission.commissioner
    commissionee = commission.offer.author
    for user in [commissioner, commissionee]:
        models.ChatParticipant.objects.create(
            chat=chat,
            participant=user
        )


def get_messages_from_chat(
        chat: 'models.Chat') -> 'Manager[models.ChatMessage]':
    return models.ChatMessage.objects.filter(chat=chat)


def get_chat_by_pk(pk) -> 'models.Chat':
    return get_object_or_404(models.Chat, pk=pk)


def test_user_is_participant_of_chat(
        chat: 'models.Chat',
        user: 'models.User') -> bool:
    return models.Chat.objects.filter(
        chatparticipant__participant=user).exists()
