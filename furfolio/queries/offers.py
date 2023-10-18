from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q


from .. import models
from .. import form_fields


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


def full_text_search_offers(text_query: str, author: str, sort: str, closed_offers: bool, consent_to_adult_content: bool):
    query = models.Offer.objects
    text_query_cleaned = text_query.strip()
    author_cleaned = author.strip()
    if text_query_cleaned:
        search_vector = SearchVector(
            "name", weight="A") + SearchVector("description", weight="A")
        search_query = SearchQuery(text_query_cleaned)
        search_rank = SearchRank(search_vector, search_query)
        query = query.annotate(rank=search_rank).filter(rank__gte=0.2)
    if author_cleaned:
        print("query:", query)
        query = query.filter(author__username=author_cleaned)
        print("query:", query)
    if not closed_offers:
        current_datetime = timezone.now()
        query = query.filter(
            cutoff_date__gt=current_datetime
        ).filter(
            forced_closed=False
        )
    if not consent_to_adult_content:
        query = query.filter(rating=models.Offer.RATING_GENERAL)
    match sort:
        case form_fields.SortField.CHOICE_RELEVANCE:
            if text_query_cleaned:
                query = query.order_by("-rank")
            else:
                query = query.order_by("-created_date")
        case form_fields.SortField.CHOICE_CREATED_DATE:
            query = query.order_by("-created_date")
        case form_fields.SortField.CHOICE_UPDATED_DATE:
            print("updated date")
            query = query.order_by("-updated_date")
        case _:
            query = query.order_by("-created_date")
    return query
