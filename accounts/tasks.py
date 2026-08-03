from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


@shared_task(bind=True,autoretry_for=(Exception,),retry_backoff=True,max_retries=3,)
def send_email_task(self,subject: str,text_message: str,html_message: str,recipient: str,) -> str:
    """
    Send an email asynchronously using Celery.
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )

    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)

    return f"Email sent to {recipient}"