from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponse as HttpResponse
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
from ..queries import users as user_queries
from ..queries import support as support_queries
from .. import forms
from .mixins import EmailsContextMixin
from .pagination import PageRangeContextMixin
from .pagination import PAGE_SIZE


# the name of the user group that is allowed permissions to CRUD support
# tickets
SUPPORT_MODERATOR_GROUP_NAME = "support_mod"


class Support(PageRangeContextMixin, generic.ListView):
    model = models.SupportTicket
    template_name = "furfolio/support/support.html"
    context_object_name = "support_tickets"
    paginate_by = PAGE_SIZE

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        # check if user is logged in. if not, redirect to the not-logged-in
        # version of this page
        if not request.user.is_authenticated:
            return redirect(reverse("support_not_logged_in"))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return support_queries.get_support_tickets_by_author(self.request.user)


class SupportNotLoggedIn(EmailsContextMixin, generic.TemplateView):
    template_name = "furfolio/support/support_not_logged_in.html"

    def get(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        # if the user is authenticated, redirect to regular support page
        if request.user.is_authenticated:
            return redirect(reverse("support"))
        else:
            return super().get(request, *args, **kwargs)


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
        elif user_queries.is_user_in_group(self.request.user, SUPPORT_MODERATOR_GROUP_NAME):
            return True
        else:
            return False

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["current_user_is_support_mod"] = user_queries.is_user_in_group(
            self.request.user, SUPPORT_MODERATOR_GROUP_NAME)
        return context


class CreateChatForSupportTicket(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        if not user_queries.is_user_in_group(
                request.user, SUPPORT_MODERATOR_GROUP_NAME):
            raise PermissionDenied(
                "You do not have permission to add a chat to this support ticket."
            )

        support_ticket = get_object_or_404(models.SupportTicket, pk=pk)
        chat_queries.create_chat_for_support_ticket(
            support_ticket, request.user)

        redirect_url = request.GET["next"]
        return redirect(redirect_url)
