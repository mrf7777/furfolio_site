from typing import Any
from django.conf import settings


class EmailsContextMixin:
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["info_email"] = settings.INFO_EMAIL
        context["support_email"] = settings.SUPPORT_EMAIL
        return context
