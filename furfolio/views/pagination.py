
from typing import Any, List
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.core.paginator import Page
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib import auth
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from honeypot.decorators import check_honeypot
from .. import models
from .. import mixins
from .. import utils
from ..queries import users as user_queries
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from ..queries import commission_messages as commission_messages_queries
from ..queries import user_following_user as user_following_user_queries
from ..queries import tags as tag_queries
from ..queries import tag_categories as tag_category_queries
from ..queries import chat as chat_queries
from .. import forms

PAGE_SIZE = 10

class PageRangeContextMixin:
    page_range_context_object_name = "page_range"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[self.page_range_context_object_name] = self.__class__.get_page_range_items(
            context["page_obj"])
        return context

    def get_page_range_items(page: Page) -> List[str]:
        """
        Given the page object, which you should get from the context, this
        will return a list of page items, including ellipsis, that you
        can then display in a template.
        """
        return list(page.paginator.get_elided_page_range(page.number))
