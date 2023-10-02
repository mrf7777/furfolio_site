from django.test import TestCase
from .models import Commission, User, Offer
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

# Create your tests here.


class LimitReviewCommissionsTestCase(TestCase):
    def setUp(self):
        self.creator = User(
            username="creator", email="creator@test.com", role=User.ROLE_CREATOR, password="2"
        )
        self.creator.full_clean()
        self.creator.save()
        self.buyer = User(
            username="buyer", email="buyer@test.com", role=User.ROLE_BUYER, password="2"
        )
        self.buyer.full_clean()
        self.buyer.save()
        self.offer = Offer(
            author=self.creator,
            name="Offer",
            description="This is a test offer to test review commissions.",
            cutoff_date=timezone.now()+datetime.timedelta(days=7),
            slots=2,
            max_review_commissions=1,
        )
        self.offer.full_clean()
        self.offer.save()

    def test_max_review_commissions(self):
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
