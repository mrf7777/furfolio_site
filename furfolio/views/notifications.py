from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponse as HttpResponse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .. import models
from ..queries import notifications as notification_queries
from .pagination import PageRangeContextMixin, PAGE_SIZE


class Notifications(
        PageRangeContextMixin,
        LoginRequiredMixin,
        generic.ListView):
    model = models.Notification
    context_object_name = "notifications"
    template_name = "furfolio/notifications/notification_list.html"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        return notification_queries.get_notifications_for_user(
            self.request.user)


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
