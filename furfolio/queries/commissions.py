
from functools import reduce
from typing import Any
from django.db.models import Q
from django.db.models import Manager
from django.shortcuts import get_object_or_404

from .. import models
from .. import form_fields


def get_commission_by_pk(pk) -> 'models.Commission':
    return get_object_or_404(models.Commission, pk=pk)


def get_commissions_for_user_as_commissioner(
        user: 'models.User',
        order_by: str = "-updated_date",
) -> 'Manager[models.Commission]':
    return models.Commission.objects.filter(
        commissioner=user,
    ).order_by(order_by)


def get_commissions_for_commissioner_and_offer(
        commissioner: 'models.User',
        offer: 'models.Offer',
) -> 'Manager[models.Commission]':
    return models.Commission.objects.filter(
        commissioner=commissioner,
        offer=offer,
    )


def get_commissions_for_user_as_offer_author(
        user: 'models.User',
        commission_states: [str],
        offer: Any | None = None,
        order_by: str = "-updated_date"
) -> 'dict[str, Manager[models.Commission]]':
    """
    Given a user and a set of commissions states, return
    a dictionary that maps from commission states to query sets
    that hold the commissions of that state for the user.
    An offer can be provided, if so, it will only return commissions
    from that offer.
    """

    querysets = dict()
    for state in commission_states:
        query = models.Commission.objects.filter(
            offer__author=user,
            state=state,
        )
        if offer is not None:
            query = query.filter(offer=offer)
        query = query.order_by(order_by)
        querysets[state] = query
    return querysets


def get_active_commissions_of_offer(offer: 'models.Offer'):
    return get_active_commissions().filter(offer=offer)


def get_commissions_in_review_for_offer(offer: 'models.Offer'):
    return models.Commission.objects.filter(offer=offer, state=models.Commission.STATE_REVIEW)


def get_active_commissions():
    query = Q(
        state=models.Commission.STATE_ACCEPTED
    ) | Q(
        state=models.Commission.STATE_IN_PROGRESS
    ) | Q(
        state=models.Commission.STATE_CLOSED
    )
    return models.Commission.objects.filter(query)


def get_commissions_with_user(user: 'models.User'):
    return models.Commission.objects.filter(Q(offer__author=user) | Q(commissioner=user))


class CommissionsSearchQuery:
    def __init__(
        self,
        current_user: 'models.User',
        sort: str = "",
        self_managed: bool = None,
        review: bool = False,
        accepted: bool = False,
        in_progress: bool = False,
        closed: bool = False,
        rejected: bool = False,
    ):
        self.current_user = current_user
        self.sort = sort
        self.self_managed = self_managed
        self.review = review
        self.accepted = accepted
        self.in_progress = in_progress
        self.closed = closed
        self.rejected = rejected


def search_commissions(search_query: CommissionsSearchQuery):
    # get commissions where current user is either buyer or creator
    query = get_commissions_with_user(search_query.current_user)
    # filter self managed
    if search_query.self_managed is True:
        query = query.filter(
            offer__author=search_query.current_user,
            commissioner=search_query.current_user
        )
    elif search_query.self_managed is False:
        query = query.exclude(
            offer__author=search_query.current_user,
            commissioner=search_query.current_user
        )
    # build filter for commission states
    state_queries = []
    if search_query.review:
        state_queries.append(Q(state=models.Commission.STATE_REVIEW))
    if search_query.accepted:
        state_queries.append(Q(state=models.Commission.STATE_ACCEPTED))
    if search_query.in_progress:
        state_queries.append(
            Q(state=models.Commission.STATE_IN_PROGRESS))
    if search_query.closed:
        state_queries.append(Q(state=models.Commission.STATE_CLOSED))
    if search_query.rejected:
        state_queries.append(Q(state=models.Commission.STATE_REJECTED))
    # state filters should be OR'ed together
    state_query = reduce(lambda q1, q2: q1 | q2, state_queries, Q())
    query = query.filter(state_query)
    # sort
    match search_query.sort:
        case form_fields.SortField.CHOICE_RELEVANCE:
            query = query.order_by("-updated_date")
        case form_fields.SortField.CHOICE_CREATED_DATE:
            query = query.order_by("-created_date")
        case form_fields.SortField.CHOICE_UPDATED_DATE:
            query = query.order_by("-updated_date")
        case _:
            query = query.order_by("-updated_date")

    return query


def commission_search_string_to_query(search_string: str, current_user: 'models.User') -> CommissionsSearchQuery:
    query = CommissionsSearchQuery(current_user)

    # search string example: "offer:34 sort:created_date state:accepted state:in_progress"
    # token examples: "sort:created_date", "offer:43", "commissioner:test"
    # the left of the colon is called the prefix
    # the right of the colon is called the suffix
    tokens = search_string.strip().split()

    for token in tokens:
        # tokens must have exactly one colon
        if token.count(":") != 1:
            continue

        prefix, suffix = token.split(":")
        match prefix.lower():
            case "sort":
                query.sort = suffix
            case "self_managed":
                match suffix.lower():
                    case "true":
                        query.self_managed = True
                    case "false":
                        query.self_managed = False
            case "state":
                match suffix.lower():
                    case "review":
                        query.review = True
                    case "accepted":
                        query.accepted = True
                    case "in_progress":
                        query.in_progress = True
                    case "finished":
                        query.closed = True
                    case "rejected":
                        query.rejected = True

    return query
