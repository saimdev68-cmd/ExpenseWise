from django.db import transaction
from accounts.constants import OTPPurpose
from accounts.models import User, PendingEmail

from .otp_services import OTPService
from .service_result import ServiceResult


class EmailChangeService:
    """
    User Email Change Service.
    """
    @staticmethod
    @transaction.atomic
    def request_email_change(user, new_email, ip):

        new_email = new_email.strip().lower()

        if user.email.lower() == new_email:
            return ServiceResult(
                success=False,
                message="This is already your current email address."
            )

        if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
            return ServiceResult(success=False,message="Email already exists.")

        pending_email, _ = PendingEmail.objects.update_or_create(
            user=user,
            defaults={
                "email": new_email,
            }
        )

        OTPService.send_otp(email=new_email,purpose=OTPPurpose.EMAIL_CHANGE,ip=ip)

        return ServiceResult(success=True,message=f"An email verification OTP has been sent to {new_email}.")