
from functools import reduce
from typing import Any
from django.db.models import Q
from django.db.models import Manager
from django.shortcuts import get_object_or_404

from .. import models


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
    return models.Commission.objects.filter(
        offer=offer, state=models.Commission.STATE_REVIEW)


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
    return models.Commission.objects.filter(
        Q(offer__author=user) | Q(commissioner=user))


class CommissionsSearchQuery:
    def __init__(
        self,
        sort: str | None = None,    # TODO: without circular import, use constant defined in Commission model
        self_managed: bool | None = None,
        review: bool = False,
        accepted: bool = False,
        in_progress: bool = False,
        closed: bool = False,
        rejected: bool = False,
        offer: int | None = None,
        order: str | None = None,   # TODO: define an order class at the query package level to handle this
        commissioner: str = "",
        creator: str = "",
    ):
        self.sort = sort
        self.self_managed = self_managed
        self.review = review
        self.accepted = accepted
        self.in_progress = in_progress
        self.closed = closed
        self.rejected = rejected
        self.offer = offer
        self.order = order
        self.commissioner = commissioner
        self.creator = creator

    def commission_search_string_to_query(
            search_string: str) -> 'CommissionsSearchQuery':
        query = CommissionsSearchQuery()

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
                case "offer":
                    try:
                        query.offer = int(suffix)
                    except ValueError:
                        pass
                case "order":
                    query.order = suffix.lower()
                case "commissioner":
                    query.commissioner = suffix
                case "creator":
                    query.creator = suffix

        return query

    def to_search_string(self) -> str:
        string = ""
        if self.sort:
            string += f"sort:{self.sort} "
        if self.self_managed is not None:
            if self.self_managed is True:
                string += f"self_managed:true "
            else:
                string += f"self_managed:false "
        if self.review:
            string += "state:review "
        if self.accepted:
            string += "state:accepted "
        if self.in_progress:
            string += "state:in_progress "
        if self.closed:
            string += "state:finished "
        if self.rejected:
            string += "state:rejected "
        if self.offer is not None:
            string += f"offer:{self.offer} "
        if self.order:
            string += f"order:{self.order} "
        if self.commissioner:
            string += f"commissioner:{self.commissioner} "
        if self.creator:
            string += f"creator:{self.creator} "

        return string.strip()


def search_commissions(search_query: CommissionsSearchQuery,
                       current_user: 'models.User'):
    # get commissions where current user is either buyer or creator
    query = get_commissions_with_user(current_user)
    # filter self managed
    if search_query.self_managed is True:
        query = query.filter(
            offer__author=current_user,
            commissioner=current_user
        )
    elif search_query.self_managed is False:
        query = query.exclude(
            offer__author=current_user,
            commissioner=current_user
        )
    # filter offer
    if search_query.offer is not None:
        query = query.filter(offer__pk=search_query.offer)
    # filter commissioner
    if search_query.commissioner:
        query = query.filter(commissioner__username=search_query.commissioner)
    # filter creator
    if search_query.creator:
        query = query.filter(offer__author__username=search_query.creator)
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
        case models.Commission.SORT_CREATED_DATE:
            query = query.order_by("created_date")
        case models.Commission.SORT_UPDATED_DATE | None:
            query = query.order_by("updated_date")
        case _:
            query = query.order_by("updated_date")
    match search_query.order:
        case "a":
            pass
        case "d" | None:
            query = query.reverse()

    return query
