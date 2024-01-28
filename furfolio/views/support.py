from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.utils.http import urlencode
from django.core.exceptions import PermissionDenied
from .. import models
from .. import utils
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from ..queries import chat as chat_queries
from ..queries import support as support_queries
from .. import forms
from .pagination import PageRangeContextMixin
from .pagination import PAGE_SIZE


class Support(LoginRequiredMixin, PageRangeContextMixin, generic.ListView):
    model = models.SupportTicket
    template_name = "furfolio/support/support.html"
    context_object_name = "support_tickets"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        return support_queries.get_support_tickets_by_author(self.request.user)


class CreateSupportTicket(LoginRequiredMixin, generic.CreateView):
    model = models.SupportTicket
    template_name = "furfolio/support/support_ticket_create.html"
    form_class = forms.SupportTicketForm

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["author"] = self.request.user.pk
        return initial


class SupportTicket(
        LoginRequiredMixin,
        UserPassesTestMixin,
        generic.DetailView):
    model = models.SupportTicket
    template_name = "furfolio/support/support_ticket_detail.html"
    context_object_name = "support_ticket"

    def test_func(self) -> bool | None:
        object = self.get_object()
        if object.author.pk == self.request.user.pk:
            return True
        else:
            return False
