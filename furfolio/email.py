from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from . import models


def send_commission_state_changed_email(new_commission: 'models.Commission'):
    text_content = render_to_string(
        "furfolio/email/commissions/commission_state_changed.txt",
        context={"commission": new_commission}
    )
    html_content = render_to_string(
        "furfolio/email/commissions/commission_state_changed.html",
        context={"commission": new_commission}
    )
    email = EmailMultiAlternatives(
        "Commission state changed",
        text_content,
        "admin@furfolio.net",
        [new_commission.commissioner.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
