from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

@shared_task
def send_password_reset_mail(subject,message,from_email,recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False
    )
    return f"Password reset email is send to {recipient_list}"

@shared_task
def send_otp_mail(subject,message,email):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )
    return f"An otp email is send to {email}"

@shared_task
def send_email_otp_mail(email,otp):
    send_mail(
        subject="Otp For Email Verification",
        message=f"Your Otp for email verification is {otp}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )
    return f"An email verification otp email is send to {email}"