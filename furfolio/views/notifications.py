from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponse as HttpResponse
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .. import models
from ..forms import NotificationSearchForm
from ..queries import notifications as notification_queries
from .pagination import PageRangeContextMixin


class Notifications(
        PageRangeContextMixin,
        LoginRequiredMixin,
        generic.ListView):
    model = models.Notification
    context_object_name = "notifications"
    template_name = "furfolio/notifications/notification_list.html"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[Any]:
        search_form = NotificationSearchForm(self.request.GET)
        if search_form.is_valid():
            show_opened = search_form.cleaned_data["opened"]
            return notification_queries.get_notifications_for_user(
                self.request.user, show_opened)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = NotificationSearchForm(self.request.GET)

        context["exists_unread_notifications"] = notification_queries.get_num_unread_notifications_for_user(
            self.request.user) > 0
        return context


class OpenNotification(
        LoginRequiredMixin,
        UserPassesTestMixin,
        generic.RedirectView):
    def get_notification(self) -> 'models.Notification':
        return notification_queries.get_notification_by_pk(self.kwargs["pk"])

    def test_func(self) -> bool | None:
        notification = self.get_notification()
        return notification.recipient.pk == self.request.user.pk

    def get_redirect_url(self, *args, **kwargs) -> str | None:
        return self.get_notification().get_content_url()

    def get(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        notification_queries.make_notification_seen(self.get_notification())
        return super().get(request, *args, **kwargs)


class OpenAllNotifications(
    LoginRequiredMixin,
    generic.View,
):
    def post(self, request):
        notification_queries.make_all_notifications_seen_for_user(request.user)
        redirect_url = request.GET["next"]
        return redirect(redirect_url)


class NotificationCountBadge(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/notification_count_component.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
