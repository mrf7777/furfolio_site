from functools import reduce
from typing import Any
from django.db.models import Q
from django.db.models import Manager
from django.shortcuts import get_object_or_404

from .. import models


def create_chat_for_commission(commission: 'models.Commission'):
    # create chat then create participants for
    # the commissioner and commissionee
    chat, _ = models.Chat.objects.get_or_create(
        name=commission.offer.name,
    )
    commissioner = commission.commissioner
    commissionee = commission.offer.author
    for user in [commissioner, commissionee]:
        models.ChatParticipant.objects.create(
            chat=chat,
            participant=user
        )
