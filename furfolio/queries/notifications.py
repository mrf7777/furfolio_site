from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Manager
from django.shortcuts import get_object_or_404
from . import chat as chat_queries
from . import offers as offer_queries
from .. import models


def create_message_notification(
        message: 'models.ChatMessage',
        recipient: 'models.User') -> 'models.ChatMessageNotification':
    notification = models.Notification.objects.create(
        recipient=recipient,
    )
    message_notification = models.ChatMessageNotification.objects.create(
        notification=notification,
        message=message,
    )
    return message_notification


def create_message_notifications_for_recipients(message: 'models.ChatMessage'):
    for recipient in chat_queries.get_recipients_of_message(message):
        create_message_notification(message, recipient)


def create_offer_posted_notification(
        offer: 'models.Offer',
        recipient: 'models.User') -> 'models.OfferPostedNotification':
    notification = models.Notification.objects.create(
        recipient=recipient,
    )
    offer_posted_notification = models.OfferPostedNotification.objects.create(
        notification=notification,
        offer=offer,
    )
    return offer_posted_notification


def create_offer_posted_notifications_for_followers(offer: 'models.Offer'):
    users_to_notify = offer_queries.get_who_to_notify_for_new_offer(offer)
    for user in users_to_notify:
        create_offer_posted_notification(offer, user)


def create_commission_state_notification(
        commission: 'models.Commission',
        recipient: 'models.User') -> 'models.CommissionStateNotification':
    notification = models.Notification.objects.create(
        recipient=recipient,
    )
    commission_state_notification = models.CommissionStateNotification.objects.create(
        notification=notification, commission=commission, state=commission.state, )
    return commission_state_notification


def create_commission_state_notification_for_commissioner(
        commission: 'models.Commission'):
    create_commission_state_notification(commission, commission.commissioner)


def create_commission_created_notification(
        commission: 'models.Commission',
        recipient: 'models.User') -> 'models.CommissionCreatedNotification':
    notification = models.Notification.objects.create(
        recipient=recipient,
    )
    commission_created_notification = models.CommissionCreatedNotification.objects.create(
        notification=notification, commission=commission, )
    return commission_created_notification


def create_commission_created_notification_for_author(
        commission: 'models.Commission'):
    create_commission_created_notification(commission, commission.offer.author)


def create_user_followed_notification(
        follower: 'models.User',
        recipient: 'models.User') -> 'models.UserFollowedNotification':
    notification = models.Notification.objects.create(
        recipient=recipient,
    )
    user_followed_notification = models.UserFollowedNotification.objects.create(
        notification=notification, follower=follower, )
    return user_followed_notification


def create_user_followed_notification_using_user_following_user(
        user_following_user: 'models.UserFollowingUser'):
    create_user_followed_notification(
        user_following_user.follower,
        user_following_user.followed)


def get_notifications_for_user(user: 'models.User') -> 'Manager[models.User]':
    return models.Notification.objects.filter(
        recipient=user).order_by("-created_date")


def get_notification_by_pk(pk) -> 'models.Notification':
    return get_object_or_404(models.Notification, pk=pk)


def make_notification_seen(notification: 'models.Notification'):
    notification.seen = True
    notification.full_clean()
    notification.save()


def get_num_unread_notifications_for_user(user: 'models.User') -> int:
    return get_notifications_for_user(user).filter(seen=False).count()
