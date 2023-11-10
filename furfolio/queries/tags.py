from functools import reduce
from typing import Any
from django.db.models import Q
from django.db.models import Manager
from django.shortcuts import get_object_or_404

from .. import models


def get_all_tags() -> 'Manager[models.Tag]':
    return models.Tag.objects.all().order_by("name")
