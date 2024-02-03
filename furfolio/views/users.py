from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .. import models
from ..queries import users as user_queries
from ..queries import user_following_user as user_following_user_queries
from .. import forms
from .pagination import PageRangeContextMixin, PAGE_SIZE


class UserMixin:
    model = models.User
    slug_field = "username"
    slug_url_kwarg = "username"


class User(UserMixin, generic.DetailView):
    context_object_name = "user"
    template_name = "furfolio/users/user_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        user_to_follow = get_object_or_404(
            models.User,
            username=self.kwargs["username"],
        )
        if self.request.user.is_authenticated:
            context["is_user_followed"] = user_following_user_queries.does_user_follow_user(
                self.request.user, user_to_follow)
        else:
            context["is_user_followed"] = None

        return context


class UpdateUserProfile(
        UserMixin,
        LoginRequiredMixin,
        UserPassesTestMixin,
        generic.UpdateView):
    template_name = "furfolio/users/user_profile_update.html"
    context_object_name = "user"
    form_class = forms.UpdateUserProfileForm

    def test_func(self):
        return self.get_object().pk == self.request.user.pk


class UpdateUserAccount(
    UserMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
    generic.UpdateView
):
    template_name = "furfolio/users/user_account_update.html"
    context_object_name = "user"
    form_class = forms.UpdateUserAccountForm

    def test_func(self) -> bool | None:
        return self.get_object().pk == self.request.user.pk


class UserList(PageRangeContextMixin, UserMixin, generic.ListView):
    context_object_name = "users"
    template_name = "furfolio/users/user_list.html"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = forms.UserSearchForm(self.request.GET)
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            return user_queries.full_text_search_creators(text_query)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = forms.UserSearchForm(self.request.GET)
        return context


class FollowedList(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = models.UserFollowingUser
    context_object_name = "followed_users"
    template_name = "furfolio/users/follow/followed_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        return self.request.user.get_followed_users()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(
            models.User, username=self.kwargs["username"])
        return context

    def test_func(self) -> bool | None:
        return self.request.user == get_object_or_404(
            models.User, username=self.kwargs["username"])


class MakeUserFollowUser(LoginRequiredMixin, generic.View):
    def post(self, request, username):
        user_to_follow = get_object_or_404(models.User, username=username)
        if user_to_follow == request.user:
            raise PermissionDenied(
                "You can not follow yourself."
            )

        user_following_user_queries.make_user_follow_or_unfollow_user(
            follower=request.user,
            followed=user_to_follow,
            should_follow=True
        )

        redirect_url = request.GET["next"]
        return redirect(redirect_url)


class MakeUserUnfollowUser(LoginRequiredMixin, generic.View):
    def post(self, request, username):
        user_to_unfollow = get_object_or_404(models.User, username=username)
        if user_to_unfollow == request.user:
            raise PermissionDenied(
                "You can not unfollow yourself."
            )

        user_following_user_queries.make_user_follow_or_unfollow_user(
            follower=request.user,
            followed=user_to_unfollow,
            should_follow=False
        )

        redirect_url = request.GET["next"]
        return redirect(redirect_url)
