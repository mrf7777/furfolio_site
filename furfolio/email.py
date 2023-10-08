from typing import Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from . import models


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
        reply_to=[settings.DEFAULT_FROM_EMAIL,],
    )
    email.attach_alternative(html_content, "text/html")
    return email.send()


def send_commission_state_changed_email(new_commission: 'models.Commission'):
    send_email(
        "furfolio/email/commissions/commission_state_changed.txt",
        "furfolio/email/commissions/commission_state_changed.html",
        {"commission": new_commission},
        "Commission state changed",
        new_commission.commissioner.email,
    )
