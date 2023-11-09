from typing import Any, List
from django import http
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.core.paginator import Page
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.core.exceptions import PermissionDenied
from .. import models
from .. import mixins
from .. import utils
from ..queries import users as user_queries
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from ..queries import commission_messages as commission_messages_queries
from ..queries import user_following_user as user_following_user_queries
from ..forms import CommissionSearchForm, CustomUserCreationForm, OfferForm, CommissionForm, UpdateUserForm, OfferFormUpdate, OfferSearchForm, UserSearchForm, UpdateCommissionForm, CommissionMessageForm, OfferSelectForm, TagForm, TagUpdateForm, TagCategoryForm


PAGE_SIZE = 10


def get_page_range_items(page: Page) -> List[str]:
    """
    Given the page object, which you should get from the context, this
    will return a list of page items, including ellipsis, that you
    can then display in a template.
    """
    return list(page.paginator.get_elided_page_range(page.number))


class Home(generic.TemplateView):
    template_name = "furfolio/home.html"

    def get(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        if self.request.user.is_authenticated:
            return redirect("dashboard")
        else:
            return super().get(request, *args, **kwargs)


class DashboardRedirector(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str | None:
        if self.request.user.role == models.User.ROLE_BUYER:
            return reverse("buyer_dashboard")
        elif self.request.user.role == models.User.ROLE_CREATOR:
            return reverse("creator_dashboard")


class CreatorDashboard(LoginRequiredMixin, generic.FormView):
    template_name = "furfolio/dashboards/creator.html"
    form_class = OfferSelectForm

    MAX_COMMISSIONS_PER_COLUMN = 15

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        relevant_offers_to_show_on_board = offer_queries.get_relevant_offers_for_user(
            self.request.user)
        offer_form = OfferSelectForm(
            queryset=relevant_offers_to_show_on_board, data=self.request.GET)
        offer_form.full_clean()
        context["offer_select_form"] = offer_form

        selected_offer = offer_form.cleaned_data.get("offer")
        commissions = commission_queries.get_commissions_for_user_as_offer_author(
            self.request.user,
            [
                models.Commission.STATE_REVIEW,
                models.Commission.STATE_ACCEPTED,
                models.Commission.STATE_IN_PROGRESS,
            ],
            selected_offer,
        )

        review_commissions = commissions[models.Commission.STATE_REVIEW]
        accepted_commissions = commissions[models.Commission.STATE_ACCEPTED]
        in_progress_commissions = commissions[models.Commission.STATE_IN_PROGRESS]

        review_commissions_total_count = review_commissions.count()
        accepted_commissions_total_count = accepted_commissions.count()
        in_progress_commissions_total_count = in_progress_commissions.count()
        context["review_commissions_total_count"] = review_commissions_total_count
        context["accepted_commissions_total_count"] = accepted_commissions_total_count
        context["in_progress_commissions_total_count"] = in_progress_commissions_total_count

        max_commissions_per_column = self.__class__.MAX_COMMISSIONS_PER_COLUMN
        context["review_commissions"] = review_commissions[:max_commissions_per_column]
        context["accepted_commissions"] = accepted_commissions[:max_commissions_per_column]
        context["in_progress_commissions"] = in_progress_commissions[:max_commissions_per_column]

        context["review_commissions_overflow"] = review_commissions_total_count > max_commissions_per_column
        context["accepted_commissions_overflow"] = accepted_commissions_total_count > max_commissions_per_column
        context["in_progress_commissions_overflow"] = in_progress_commissions_total_count > max_commissions_per_column

        # construct urls to commission searches for each column so that the
        # user can "see all"
        review_commissions_query = commission_queries.CommissionsSearchQuery(
            review=True,
            offer=selected_offer.pk if selected_offer else None,
        )
        review_commissions_query_url = \
            reverse("commissions") \
            + "?" \
            + urlencode({"search": review_commissions_query.to_search_string()})
        context["see_review_commissions_url"] = review_commissions_query_url

        accepted_commissions_query = commission_queries.CommissionsSearchQuery(
            accepted=True,
            offer=selected_offer.pk if selected_offer else None,
        )
        accepted_commissions_query_url = \
            reverse("commissions") \
            + "?" \
            + urlencode({"search": accepted_commissions_query.to_search_string()})
        context["see_accepted_commissions_url"] = accepted_commissions_query_url

        in_progress_commissions_query = commission_queries.CommissionsSearchQuery(
            in_progress=True,
            offer=selected_offer.pk if selected_offer else None,
        )
        in_progress_commissions_query_url = reverse("commissions") + "?" + urlencode(
            {"search": in_progress_commissions_query.to_search_string()})
        context["see_in_progress_commissions_url"] = in_progress_commissions_query_url

        return context


class BuyerDashboard(LoginRequiredMixin, generic.ListView):
    template_name = "furfolio/dashboards/buyer.html"
    context_object_name = "commissions"
    model = models.Commission
    paginate_by = PAGE_SIZE

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_range"] = get_page_range_items(context["page_obj"])
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return commission_queries.get_commissions_for_user_as_commissioner(
            self.request.user)


class OfferList(mixins.GetAdultConsentMixin, generic.ListView):
    model = models.Offer
    template_name = "furfolio/offers/offer_list.html"
    context_object_name = "offer_list"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = OfferSearchForm(self.request.GET)
        consent_to_adult_content = self.does_user_consent_to_adult_content()
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            author = search_form.cleaned_data["author"].strip()
            sort = search_form.cleaned_data["sort"]
            closed_offers = search_form.cleaned_data["closed_offers"]
            price_min = search_form.cleaned_data["price_min"]
            price_max = search_form.cleaned_data["price_max"]

            offer_query = offer_queries.OfferSearchQuery(
                text_query=text_query,
                sort=sort,
                author=author,
                closed_offers=closed_offers,
                price_min=price_min,
                price_max=price_max,
                consent_to_adult_content=consent_to_adult_content
            )

            return offer_queries.full_text_search_offers(offer_query)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = OfferSearchForm(self.request.GET)
        context["page_range"] = get_page_range_items(context["page_obj"])
        return context


class Offer(mixins.GetAdultConsentMixin,
            UserPassesTestMixin, generic.DetailView):
    model = models.Offer
    context_object_name = "offer"
    template_name = "furfolio/offers/offer_detail.html"

    def test_func(self) -> bool | None:
        match self.get_object().rating:
            case models.RATING_GENERAL:
                return True
            case models.RATING_ADULT:
                return self.does_user_consent_to_adult_content()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["should_show_create_commission_button"] = self.should_show_create_commission_button()

        offer: models.Offer = self.get_object()
        commissions_of_offer_query = commission_queries.CommissionsSearchQuery(
            offer=offer.pk
        )
        commissions_of_offer_url = reverse("commissions") + "?" + urlencode(
            {"search": commissions_of_offer_query.to_search_string()})
        context["see_commissions_url"] = commissions_of_offer_url

        if self.request.user == offer.author:
            tweet_text = f"You can commission my new offer \"{offer.name}\" at Furfolio."
        else:
            tweet_text = f"You can commission the offer \"{offer.name}\" by \"{offer.author.username}\" at Furfolio."
        context["tweet_text"] = tweet_text

        return context

    def should_show_create_commission_button(self) -> bool:
        offer = self.get_object()
        if self.request.user.is_authenticated:
            return self.request.user.can_commission_offer(offer)
        else:
            return None


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CreateOffer(LoginRequiredMixin, generic.CreateView):
    model = models.Offer
    form_class = OfferForm
    template_name = "furfolio/offers/offer_form.html"

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["author"] = self.request.user
        return initial


class UpdateOffer(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Offer
    form_class = OfferFormUpdate
    template_name = "furfolio/offers/offer_update_form.html"

    # TODO: use the slightly more efficient version
    # https://www.django-antipatterns.com/antipattern/checking-ownership-through-the-userpassestestmixin.html
    def test_func(self):
        return self.get_object().author.pk == self.request.user.pk


class DeleteOffer(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = models.Offer
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "furfolio/offers/offer_delete.html"
    success_url = reverse_lazy("offer_list")

    def test_func(self):
        return self.get_object().author.pk == self.request.user.pk


class User(generic.DetailView):
    model = models.User
    slug_field = "username"
    slug_url_kwarg = "username"
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


class UpdateUser(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.User
    form_class = CustomUserCreationForm
    template_name = "furfolio/users/user_update.html"
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"
    form_class = UpdateUserForm

    def test_func(self):
        return self.get_object().pk == self.request.user.pk


class UserList(generic.ListView):
    model = models.User
    context_object_name = "users"
    template_name = "furfolio/users/user_list.html"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = UserSearchForm(self.request.GET)
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            return user_queries.full_text_search_creators(text_query)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET)
        context["page_range"] = get_page_range_items(context["page_obj"])
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


class CreateCommission(LoginRequiredMixin, generic.CreateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_create.html"
    form_class = CommissionForm

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


class Commissions(LoginRequiredMixin, generic.ListView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_list.html"
    context_object_name = "commissions"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        form = CommissionSearchForm(self.request.GET)
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
        if self.request.GET & CommissionSearchForm.base_fields.keys():
            search_form = CommissionSearchForm(self.request.GET)
        else:
            search_form = CommissionSearchForm()
        context["form"] = search_form
        context["page_range"] = get_page_range_items(context["page_obj"])
        return context


class UpdateCommission(
        LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_update.html"
    form_class = UpdateCommissionForm
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
    form_class = CommissionMessageForm
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


class CreateTag(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.CreateView):
    model = models.Tag
    form_class = TagForm
    template_name = "furfolio/tags/tag_create.html"
    permission_required = "furfolio.add_tag"

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["author"] = self.request.user.id
        return initial


class UpdateTag(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.UpdateView):
    model = models.Tag
    slug_field = "name"
    slug_url_kwarg = "name"
    form_class = TagUpdateForm
    template_name = "furfolio/tags/tag_update.html"
    permission_required = "furfolio.change_tag"


class DeleteTag(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.DeleteView):
    model = models.Tag
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "furfolio/tags/tag_delete.html"
    permission_required = "furfolio.delete_tag"
    success_url = reverse_lazy("tags")


class Tag(generic.DetailView):
    model = models.Tag
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "furfolio/tags/tag_detail.html"
    context_object_name = "tag"


class TagList(generic.ListView):
    model = models.Tag
    template_name = "furfolio/tags/tag_list.html"
    context_object_name = "tags"
    paginate_by = 25

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_range"] = get_page_range_items(context["page_obj"])
        return context

    def get_queryset(self) -> QuerySet[Any]:
        # TODO: move tag query logic to tag query module
        return models.Tag.objects.all().order_by("-updated_date")


class CreateTagCategory(LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.CreateView):
    model = models.TagCategory
    template_name = "furfolio/tags/categories/category_create.html"
    form_class = TagCategoryForm
    permission_required = "furfolio.add_tagcategory"


class TagCategory(generic.DetailView):
    model = models.TagCategory
    template_name = "furfolio/tags/categories/category_detail.html"
    slug_field = "name"
    slug_url_kwarg = "name"
    context_object_name = "tag_category"


class TagCategoryList(generic.ListView):
    model = models.TagCategory
    template_name = "furfolio/tags/categories/category_list.html"
    context_object_name = "tag_categories"

    def get_queryset(self) -> QuerySet[Any]:
        # TODO: move tag category query logic to tag category query module
        return models.TagCategory.objects.all().order_by("name")
    

class UpdateTagCategory(LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.UpdateView):
    model = models.TagCategory
    slug_field = "name"
    slug_url_kwarg = "name"
    form_class = TagCategoryForm
    template_name = "furfolio/tags/categories/category_update.html"
    context_object_name = "tag_category"
    permission_required = "furfolio.change_tagcategory"
    

class DeleteTagCategory(LoginRequiredMixin,
        PermissionRequiredMixin,
        generic.DeleteView):
    model = models.TagCategory
    slug_field = "name"
    slug_url_kwarg = "name"
    template_name = "furfolio/tags/categories/category_delete.html"
    permission_required = "furfolio.delete_tagcategory"
    success_url = reverse_lazy("tag_categories")