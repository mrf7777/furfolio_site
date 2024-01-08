from typing import Any
from django.db.models.query import QuerySet
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .. import models
from ..queries import notifications as notification_queries
from .pagination import PageRangeContextMixin, PAGE_SIZE

class Notifications(PageRangeContextMixin, LoginRequiredMixin, generic.ListView):
    model = models.Notification
    context_object_name = "notifications"
    template_name = "furfolio/notifications/notification_list.html"
    paginate_by = PAGE_SIZE
    
    def get_queryset(self) -> QuerySet[Any]:
        return notification_queries.get_notifications_for_user(self.request.user)