
from functools import reduce
from typing import Any
from django.db.models import Q
from django.db.models import Manager
from django.shortcuts import get_object_or_404

from .. import models


def get_support_tickets_by_author(author: 'models.User') -> 'Manager[models.SupportTicket]':
    return models.SupportTicket.objects.filter(
        author=author,
    ).order_by("-created_date")