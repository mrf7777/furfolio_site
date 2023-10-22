
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Manager

from .. import models


def full_text_search_creators(text_query: str):
    text_query_cleaned = text_query.strip()
    query = models.User.objects
    if text_query_cleaned:
        search_vector = SearchVector("username", weight="A")
        search_query = SearchQuery(text_query_cleaned)
        search_rank = SearchRank(search_vector, search_query)
        query = models.User.objects.annotate(
            rank=search_rank
        ).filter(rank__gte=0.2)
    query = query.filter(role=models.User.ROLE_CREATOR).filter(is_active=True)
    if text_query_cleaned:
        query = query.order_by("-rank")
    else:
        query = query.order_by("-date_joined")
    return query


def get_users_following_user(user: 'models.User') -> 'Manager[models.User]':
    query = models.User.objects.filter(follower__followed=user).order_by("username").distinct()
    print("get users following user query:", query)
    return query


def get_followed_users(user: 'models.User') -> 'Manager[models.User]':
    query = models.User.objects.filter(followed__follower=user).order_by("username").distinct()
    return query