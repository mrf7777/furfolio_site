from .. import models


def make_user(username, password="admin", role=models.User.ROLE_BUYER, email="test@furfolio.net"):
    user = models.User(
        username=username,
        password=password,
        role=role,
        email=email
    )
    user.full_clean()
    user.save()
    return user


def make_offer(user, name: str = "Offer", description: str = "This is an offer made by a user.", slots=3, max_review_commissions=2, forced_closed=False):
    offer = models.Offer(
        author=user,
        name=name,
        description=description,
        slots=slots,
        max_review_commissions=max_review_commissions,
        forced_closed=forced_closed,
    )
    offer.full_clean()
    offer.save()
    return offer


def make_commission(commissioner, offer, request_text="I want a commission.", state=models.Commission.STATE_REVIEW):
    commission = models.Commission(
        commissioner=commissioner,
        offer=offer,
        initial_request_text=request_text,
        state=state,
    )
    commission.full_clean()
    commission.save()
    return commission


def make_commission_message(author, commission, message):
    commission_message = models.CommissionMessage(
        commission=commission,
        author=author,
        message=message
    )
    commission_message.full_clean()
    commission_message.save()
    return commission_message
