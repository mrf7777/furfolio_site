from typing import Any
from django.conf import settings


def add_domain_and_scheme_to_url(url: str) -> str:
    return "{}{}".format(settings.DOMAIN_AND_SCHEME, url)
