from typing import Any
from django.conf import settings
from . import models

def add_domain_and_scheme_to_url(url: str) -> str:
    return "{}{}".format(settings.DOMAIN_AND_SCHEME, url)


def get_other_user_in_commission(user: 'models.User', commission: 'models.Commission') -> 'models.User':
    if user.pk == commission.commissioner.pk:
        return commission.offer.author
    elif user.pk == commission.offer.author.pk:
        return commission.commissioner