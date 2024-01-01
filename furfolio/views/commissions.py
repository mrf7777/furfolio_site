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
from ..queries import commission_messages as commission_messages_queries
from ..queries import chat as chat_queries
from .. import forms
from .pagination import PageRangeContextMixin
from .pagination import PAGE_SIZE

class CreateCommission(LoginRequiredMixin, generic.CreateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_create.html"
    form_class = forms.CommissionForm

    # prefill offer and commissioner for the commission since these are hidden
    # fields
    def get_initial(self):
        initial = super().get_initial()
        initial["offer"] = self.kwargs["offer_pk"]
        initial["commissioner"] = self.request.user.pk
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = offer_queries.get_offer_by_pk(
            self.kwargs["offer_pk"])
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)

        # if not self-managed commission, create a chat
        commission: 'models.Commission' = self.object
        if not commission.is_self_managed():
            chat_queries.create_chat_for_commission(commission)

        return response


class Commission(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_detail.html"
    context_object_name = "commission"

    def test_func(self):
        object = self.get_object()
        if object.offer.author.pk == self.request.user.pk:
            return True
        elif object.commissioner.pk == self.request.user.pk:
            return True
        else:
            return False


class Commissions(PageRangeContextMixin, LoginRequiredMixin, generic.ListView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_list.html"
    context_object_name = "commissions"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        form = forms.CommissionSearchForm(self.request.GET)
        if form.is_valid():
            return commission_queries.search_commissions(
                commission_queries.CommissionsSearchQuery.commission_search_string_to_query(
                    form.cleaned_data["search"], ), current_user=self.request.user)
        else:
            return models.Commission.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search_form = None
        # https://stackoverflow.com/a/43096716
        if self.request.GET & forms.CommissionSearchForm.base_fields.keys():
            search_form = forms.CommissionSearchForm(self.request.GET)
        else:
            search_form = forms.CommissionSearchForm()
        context["form"] = search_form
        return context

    def url_for_query(query: commission_queries.CommissionsSearchQuery) -> str:
        return \
            reverse("commissions") \
            + "?" \
            + urlencode({"search": query.to_search_string()})


class UpdateCommission(
        LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_update.html"
    form_class = forms.UpdateCommissionForm
    context_object_name = "commission"

    # only let the offer author update the commission
    def test_func(self):
        return self.get_object().offer.author.pk == self.request.user.pk


class UpdateCommissionStatus(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        commission = get_object_or_404(models.Commission, pk=pk)
        # ensure that offer author only has permission to update commission
        # state
        user = self.request.user
        if user.pk != commission.offer.author.pk:
            raise PermissionDenied(
                "You do not have the permission to change the state of this commission."
            )

        redirect_url = request.GET["next"]
        commission.state = request.POST["state"]
        commission.save()
        return redirect(redirect_url)

class CommissionChat(LoginRequiredMixin,
                     UserPassesTestMixin, generic.CreateView):
    model = models.CommissionMessage
    form_class = forms.CommissionMessageForm
    template_name = "furfolio/commissions/chat/chat.html"

    def get_commission(self):
        return commission_queries.get_commission_by_pk(self.kwargs["pk"])

    def get_initial(self) -> dict[str, Any]:
        commission = self.get_commission()
        initial = super().get_initial()
        initial["commission"] = commission
        initial["author"] = self.request.user
        return initial

    def test_func(self):
        object = self.get_commission()
        if object.is_self_managed():
            return False
        elif object.offer.author.pk == self.request.user.pk:
            return True
        elif object.commissioner.pk == self.request.user.pk:
            return True
        else:
            return False

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        commission = self.get_commission()
        context["commission_messages"] = commission_messages_queries.get_commission_messages_for_commission(
            commission)
        context["other_user"] = utils.get_other_user_in_commission(
            self.request.user, commission)
        return context


