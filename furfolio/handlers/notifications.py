from django.dispatch import receiver
from django.db.models.signals import post_delete
from ..models import UserFollowedNotification, ChatMessageNotification, OfferPostedNotification, CommissionStateNotification, CommissionCreatedNotification


@receiver(post_delete, sender=ChatMessageNotification)
def delete_chat_message_notification_parent(sender, instance, **kwargs):
    if instance.notification:
        instance.notification.delete()


@receiver(post_delete, sender=OfferPostedNotification)
def delete_offer_posted_notification_parent(sender, instance, **kwargs):
    if instance.notification:
        instance.notification.delete()


@receiver(post_delete, sender=CommissionStateNotification)
def delete_commission_state_notification_parent(sender, instance, **kwargs):
    if instance.notification:
        instance.notification.delete()


@receiver(post_delete, sender=CommissionCreatedNotification)
def delete_commission_created_notification_parent(sender, instance, **kwargs):
    if instance.notification:
        instance.notification.delete()


@receiver(post_delete, sender=UserFollowedNotification)
def delete_user_followed_notification_parent(sender, instance, **kwargs):
    if instance.notification:
        instance.notification.delete()