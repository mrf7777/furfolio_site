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
from .pagination import PageRangeContextMixin, PAGE_SIZE

class TagMixin:
    model = models.Tag
    slug_field = "name"
    slug_url_kwarg = "name"


class CreateTag(
        TagMixin,
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.CreateView):
    form_class = forms.TagForm
    template_name = "furfolio/tags/tag_create.html"
    permission_required = "furfolio.add_tag"

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["author"] = self.request.user.id
        return initial


class UpdateTag(
        TagMixin,
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.UpdateView):
    form_class = forms.TagUpdateForm
    template_name = "furfolio/tags/tag_update.html"
    permission_required = "furfolio.change_tag"


class DeleteTag(
        TagMixin,
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.DeleteView):
    template_name = "furfolio/tags/tag_delete.html"
    permission_required = "furfolio.delete_tag"
    success_url = reverse_lazy("tags")


class Tag(TagMixin, generic.DetailView):
    template_name = "furfolio/tags/tag_detail.html"
    context_object_name = "tag"


class TagList(PageRangeContextMixin, TagMixin, generic.ListView):
    template_name = "furfolio/tags/tag_list.html"
    context_object_name = "tags"
    paginate_by = 25

    def get_queryset(self) -> QuerySet[Any]:
        return tag_queries.get_all_tags()


class TagCategoryMixin:
    model = models.TagCategory
    slug_field = "name"
    slug_url_kwarg = "name"


class CreateTagCategory(
        TagCategoryMixin,
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.CreateView):
    template_name = "furfolio/tags/categories/category_create.html"
    form_class = forms.TagCategoryForm
    permission_required = "furfolio.add_tagcategory"


class TagCategory(TagCategoryMixin, generic.DetailView):
    template_name = "furfolio/tags/categories/category_detail.html"
    context_object_name = "tag_category"


class TagCategoryList(TagCategoryMixin, generic.ListView):
    template_name = "furfolio/tags/categories/category_list.html"
    context_object_name = "tag_categories"

    def get_queryset(self) -> QuerySet[Any]:
        return tag_category_queries.get_all_tag_categories()


class UpdateTagCategory(
        TagCategoryMixin,
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.UpdateView):
    form_class = forms.TagCategoryForm
    template_name = "furfolio/tags/categories/category_update.html"
    context_object_name = "tag_category"
    permission_required = "furfolio.change_tagcategory"


class DeleteTagCategory(
        TagCategoryMixin,
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.DeleteView):
    template_name = "furfolio/tags/categories/category_delete.html"
    permission_required = "furfolio.delete_tagcategory"
    success_url = reverse_lazy("tag_categories")
