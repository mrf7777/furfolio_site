from .. import models


def make_user(
        username,
        password="admin",
        role=models.User.ROLE_BUYER,
        email="test@furfolio.net",
        consent_to_adult=False):
    user = models.User(
        username=username,
        password=password,
        role=role,
        email=email,
        consent_to_adult_content=consent_to_adult,
    )
    user.full_clean()
    user.save()
    return user


def make_user_follow_user(follower, followed):
    record = models.UserFollowingUser(follower=follower, followed=followed)
    record.full_clean()
    record.save()


def make_offer(
        user,
        name: str = "Offer",
        description: str = "This is an offer made by a user.",
        slots=3,
        max_review_commissions=2,
        forced_closed=False,
        max_commissions_per_user=1,
        validate=True,
        rating=models.RATING_GENERAL):
    offer = models.Offer(
        author=user,
        name=name,
        description=description,
        slots=slots,
        max_review_commissions=max_review_commissions,
        forced_closed=forced_closed,
        max_commissions_per_user=max_commissions_per_user,
        rating=rating,
    )
    if validate:
        offer.full_clean()
    offer.save()
    return offer


def make_commission(
        commissioner,
        offer,
        request_text="I want a commission.",
        state=models.Commission.STATE_REVIEW,
        validate: bool = True):
    commission = models.Commission(
        commissioner=commissioner,
        offer=offer,
        initial_request_text=request_text,
        state=state,
    )
    if validate:
        commission.full_clean()
    commission.save()
    return commission


def make_chat(
    name="Chat"
):
    chat = models.Chat(name=name)
    chat.full_clean()
    chat.save()
    return chat

def add_chat_participant(
    chat,
    user,
):
    participation = models.ChatParticipant(chat=chat, participant=user)
    participation.full_clean()
    participation.save()
    return participation

def make_chat_message(
    chat,
    author,
    message="Test message.",
):
    message = models.ChatMessage(chat=chat, author=author, message=message)
    message.full_clean()
    message.save()
    return message