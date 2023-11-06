from token import MINUS
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .. import models


def get_offer_by_pk(pk) -> 'models.Offer':
    return get_object_or_404(
        models.Offer, pk=pk)


def get_relevant_offers_for_user(user: 'models.User'):
    return models.OfferDescriptiveStrForCreator.objects.filter(
        Q(commission__state=models.Commission.STATE_REVIEW)
        | Q(commission__state=models.Commission.STATE_ACCEPTED)
        | Q(commission__state=models.Commission.STATE_IN_PROGRESS)
    ).distinct().filter(author=user)


def get_active_offers_for_user(user: 'models.User'):
    current_time = timezone.now()
    return models.Offer.objects.filter(
        cutoff_date__gte=current_time,
        forced_closed=False,
        author=user,
    )


def get_who_to_notify_for_new_offer(offer: 'models.Offer'):
    # Users who follow the offer author that do not consent to
    # seeing adult content should not receive a notification
    # about an adult offer.
    if offer.rating == models.Offer.RATING_ADULT:
        following_users = offer.author.get_following_users().filter(
            consent_to_adult_content=True)
    else:
        following_users = offer.author.get_following_users()
    return following_users


class OfferSearchQuery:
    def __init__(
        self,
        text_query: str = "",
        sort: str = "",
        author: str = "",
        closed_offers: bool = False,
        consent_to_adult_content: bool = False,
        price_min: int | None = None,
        price_max: int | None = None,
    ):
        self.text_query = text_query
        self.sort = sort
        self.author = author
        # convert (None | bool) to bool
        self.closed_offers = closed_offers and True
        self.consent_to_adult_content = consent_to_adult_content
        self.price_min = price_min
        self.price_max = price_max


def full_text_search_offers(search_query: OfferSearchQuery):
    query = models.Offer.objects
    text_query_cleaned = search_query.text_query.strip()
    author_cleaned = search_query.author.strip()
    if text_query_cleaned:
        search_vector = SearchVector(
            "name", weight="A") + SearchVector("description", weight="A")
        search_query_db = SearchQuery(text_query_cleaned)
        search_rank = SearchRank(search_vector, search_query_db)
        query = query.annotate(rank=search_rank).filter(rank__gte=0.2)
    if author_cleaned:
        query = query.filter(author__username=author_cleaned)
    if not search_query.closed_offers:
        current_datetime = timezone.now()
        query = query.filter(
            cutoff_date__gt=current_datetime
        ).filter(
            forced_closed=False
        )
    if not search_query.consent_to_adult_content:
        query = query.filter(rating=models.Offer.RATING_GENERAL)

    # filter based on price
    price_min = search_query.price_min if search_query.price_min else 0
    price_max = search_query.price_max if search_query.price_max else models.Offer.HIGHEST_PRICE
    # use range overlap formula: https://stackoverflow.com/a/3269471
    query = query.filter(min_price__lte=price_max, max_price__gte=price_min)

    match search_query.sort:
        case models.Offer.SORT_RELEVANCE:
            if text_query_cleaned:
                query = query.order_by("-rank")
            else:
                query = query.order_by("-created_date")
        case models.Offer.SORT_CREATED_DATE:
            query = query.order_by("-created_date")
        case models.Offer.SORT_UPDATED_DATE:
            print("updated date")
            query = query.order_by("-updated_date")
        case _:
            query = query.order_by("-created_date")
    return query
