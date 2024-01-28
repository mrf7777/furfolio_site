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
):
    chat = models.Chat()
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


def make_notification(
    recipient,
    seen=False,
):
    notification = models.Notification(recipient=recipient, seen=seen)
    notification.full_clean()
    notification.save()
    return notification


def make_chat_message_notification(
    notification,
    message,
):
    notification = models.ChatMessageNotification(
        notification=notification, message=message)
    notification.full_clean()
    notification.save()
    return notification


def make_offer_posted_notification(
    notification,
    offer,
):
    notification = models.OfferPostedNotification(
        notification=notification, offer=offer)
    notification.full_clean()
    notification.save()
    return notification


def make_commission_state_notification(
    notification,
    commission,
    commission_state,
):
    notification = models.CommissionStateNotification(
        notification=notification,
        commission=commission,
        commission_state=commission_state)
    notification.full_clean()
    notification.save()
    return notification


def make_commission_created_notification(
    notification,
    commission,
):
    notification = models.CommissionCreatedNotification(
        notification=notification, commission=commission)
    notification.full_clean()
    notification.save()
    return notification


def make_user_followed_notification(
    notification,
    follower,
):
    notification = models.UserFollowedNotification(
        notification=notification, follower=follower)
    notification.full_clean()
    notification.save()
    return notification
