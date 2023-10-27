from ctypes import util
from django.test import TestCase
from ..models import Commission, User, Offer
from django.utils import timezone
from django.core.exceptions import ValidationError
from . import utils
from .. import utils as furfolio_utils
from ..queries import commissions as commission_queries
import datetime


class LimitReviewCommissionsTestCase(TestCase):
    def setUp(self):
        self.creator = User(
            username="creator",
            email="creator@test.com",
            role=User.ROLE_CREATOR,
            password="2")
        self.creator.full_clean()
        self.creator.save()
        self.buyer = User(
            username="buyer",
            email="buyer@test.com",
            role=User.ROLE_BUYER,
            password="2")
        self.buyer.full_clean()
        self.buyer.save()
        cutoff_date = timezone.now() + datetime.timedelta(days=7)
        self.offer = Offer(
            author=self.creator,
            name="Offer",
            description="This is a test offer to test review commissions.",
            cutoff_date=cutoff_date,
            slots=2,
            max_review_commissions=1,
        )
        self.offer.full_clean()
        self.offer.save()

    def test_max_review_commissions_different_buyer(self):
        commission1 = Commission(
            commissioner=self.buyer,
            offer=self.offer,
            initial_request_text="This is commission 1.",
        )
        commission1.full_clean()
        commission1.save()
        commission2 = Commission(
            commissioner=self.buyer,
            offer=self.offer,
            initial_request_text="This is commission 2.",
        )
        with self.assertRaises(ValidationError):
            commission2.full_clean()

    def test_max_review_commissions_creator_is_buyer(self):
        commission1 = Commission(
            commissioner=self.creator,
            offer=self.offer,
            initial_request_text="This is commission 1.",
        )
        commission1.full_clean()
        commission1.save()
        commission2 = Commission(
            commissioner=self.creator,
            offer=self.offer,
            initial_request_text="This is commission 2.",
        )
        commission2.full_clean()
        commission2.save()
        self.assertEqual(Commission.objects.all().count(), 2)


class GetOtherUserInCommissionTestCase(TestCase):
    def setUp(self):
        self.creator = utils.make_user("creator", role=User.ROLE_CREATOR)
        self.buyer = utils.make_user("buyer", role=User.ROLE_BUYER)
        self.offer = utils.make_offer(self.creator)
        self.commission = utils.make_commission(self.buyer, self.offer)
        self.commission_self_managed = utils.make_commission(
            self.creator, self.offer)

    def test_commission_get_other_user(self):
        other_user = furfolio_utils.get_other_user_in_commission(
            self.creator, self.commission)
        self.assertEqual(other_user, self.buyer)
        other_user_2 = furfolio_utils.get_other_user_in_commission(
            self.buyer, self.commission)
        self.assertEqual(other_user_2, self.creator)

    def test_self_managed_commission_get_other_user(self):
        other_user = furfolio_utils.get_other_user_in_commission(
            self.creator, self.commission_self_managed)
        self.assertEqual(other_user, self.creator)


class MaxCommissionLimitPerUserTestCase(TestCase):
    def setUp(self) -> None:
        self.creator = utils.make_user(
            "creator", role=User.ROLE_CREATOR, email="creator@test.com")
        self.buyer = utils.make_user(
            "buyer", role=User.ROLE_BUYER, email="buyer@test.com")
        self.offer = utils.make_offer(self.creator, max_commissions_per_user=1)

    def test_commission_limit_for_buyer(self):
        utils.make_commission(self.buyer, self.offer)
        with self.assertRaises(ValidationError):
            utils.make_commission(self.buyer, self.offer)

    def test_commission_limit_does_not_apply_to_self_managed(self):
        utils.make_commission(self.creator, self.offer)
        utils.make_commission(self.creator, self.offer)


class CommissionQueryTestCase(TestCase):
    def test_filters_in_commission_query_string(self):
        query_string = "self_managed:true state:review state:accepted state:in_progress state:finished state:rejected offer:1 sort:created_date"
        query = commission_queries.CommissionsSearchQuery.commission_search_string_to_query(
            query_string)
        self.assertEqual(query.review, True)
        self.assertEqual(query.self_managed, True)
        self.assertEqual(query.offer, 1)

    def test_bad_offer_in_commission_query_string(self):
        query_string = "offer:abc123"
        query = commission_queries.CommissionsSearchQuery.commission_search_string_to_query(
            query_string)
        self.assertEqual(query.offer, None)

    def test_not_self_managed_commission_query_string(self):
        query_string = "self_managed:false"
        query = commission_queries.CommissionsSearchQuery.commission_search_string_to_query(
            query_string)
        self.assertEqual(query.self_managed, False)

    def test_useless_commission_query_string(self):
        query_string = " ffjsdlf  d:a:a 33!@#$%^&*()_::LOIJ(OL:)    "
        query = commission_queries.CommissionsSearchQuery.commission_search_string_to_query(
            query_string)
        self.assertEqual(query.review, False)
        self.assertEqual(query.accepted, False)
        self.assertEqual(query.in_progress, False)
        self.assertEqual(query.closed, False)
        self.assertEqual(query.rejected, False)
        self.assertEqual(query.sort, "")
        self.assertEqual(query.offer, None)
        self.assertEqual(query.self_managed, None)

    def test_positive_commission_query_to_search_string(self):
        query = commission_queries.CommissionsSearchQuery(
            sort="created_date",
            self_managed=True,
            review=True,
            accepted=True,
            in_progress=True,
            closed=True,
            rejected=True,
            offer=1,
        )
        query_string = query.to_search_string()
        # TODO: make tests

    def test_negative_commission_query_to_search_string(self):
        query = commission_queries.CommissionsSearchQuery(
            self_managed=False,
            review=False,
            accepted=False,
            in_progress=False,
            closed=False,
            rejected=False,
        )
        query_string = query.to_search_string()
        # TODO: make tests
