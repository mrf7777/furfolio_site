from functools import reduce
from typing import Any
from django.db.models import Q
from django.db.models import Manager
from django.shortcuts import get_object_or_404

from .. import models


def get_commission_messages_for_commission(
        commission: 'models.Commission'
) -> 'Manager[models.CommissionMessage]':
    return models.CommissionMessage.objects.filter(
        commission=commission
    ).order_by("created_date")
