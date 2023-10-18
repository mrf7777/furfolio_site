
from django.db.models import Q

from .. import models


def get_active_commissions_of_offer(offer: 'models.Offer'):
    return get_active_commissions().filter(offer=offer)


def get_active_commissions():
    query = Q(
        state=models.Commission.STATE_ACCEPTED
    ) | Q(
        state=models.Commission.STATE_IN_PROGRESS
    ) | Q(
        state=models.Commission.STATE_CLOSED
    )
    return models.Commission.objects.filter(query)
