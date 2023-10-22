from typing import Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Manager

from . import models


def truncate_string(s: str, max_length: int) -> str:
    trailing_string = ".."
    truncated = (s[:max_length - len(trailing_string)] +
                 "..") if len(s) > max_length else s
    return truncated


def send_email(
    text_template_path: str,
    html_template_path: str,
    context: dict[str, Any],
    subject: str,
    to_address: str,
) -> int:
    text_content = render_to_string(
        text_template_path,
        context=context,
    )
    html_content = render_to_string(
        html_template_path,
        context=context,
    )
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [to_address,],
        reply_to=[settings.REPLY_EMAIL,],
    )
    email.attach_alternative(html_content, "text/html")
    return email.send()


def send_commission_state_changed_email(new_commission: 'models.Commission'):
    send_email(
        "furfolio/email/commissions/commission_state_changed.txt",
        "furfolio/email/commissions/commission_state_changed.html",
        {"commission": new_commission},
        f"Commission State Changed | {new_commission.offer.name}",
        new_commission.commissioner.email,
    )


def send_new_commission_message_email(commission_message: 'models.CommissionMessage'):
    truncated_message = truncate_string(commission_message.message, 40)
    subject = f"You Got a Message | {truncated_message}"
    send_email(
        "furfolio/email/commission_messages/new_commission_message.txt",
        "furfolio/email/commission_messages/new_commission_message.html",
        {"message": commission_message},
        subject,
        commission_message.get_receiving_user().email,
    )


def send_new_offer_email(new_offer: 'models.Offer'):
    truncated_offer_title = truncate_string(new_offer.name, 23)
    author_username = truncate_string(new_offer.author.username, 20)
    subject = f"{author_username} Made an Offer | {truncated_offer_title}"
    # TODO: see if there is an efficient bulk email
    for user in new_offer.author.get_following_users():
        send_email(
            "furfolio/email/offers/offer_created.txt",
            "furfolio/email/offers/offer_created.html",
            {"offer": new_offer},
            subject,
            user.email,
        )