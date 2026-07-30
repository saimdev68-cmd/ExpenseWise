from accounts.models import User
from .otp_services import OTPService
from django.db import transaction, IntegrityError
from .service_result import ServiceResult
from accounts.caches.otp_caches import OTPCache


class RegisterService:

    @staticmethod
    def register_user(data,purpose,ip):
        email = data.get("email")
        password = data.get("password1")
        name = data.get("name")
        cooldown = OTPCache.retrieve_otp_cooldown_expiry(ip,email)
        blocked = OTPCache.retrieve_otp_verification_block(ip,email)
        ip_cooldown = OTPCache.retrieve_ip_cooldown_expiry(ip)
        ip_blocked = OTPCache.retrieve_ip_block(ip)
        if not ip_cooldown:
            OTPCache.remove_ip_block(ip)
        if ip_blocked:
            return ServiceResult(
                success=False,
                message="Please wait a few minutes and try again due to maximum otp limits."
            )
        if blocked:
            return ServiceResult(
                success=False,
                message="Please wait a few seconds and try again due to maximum attempts reached."
            )
        if cooldown:
            return ServiceResult(
                success = False,
                message = "Please wait a few seconds and try again."
            )
        if User.objects.filter(email=email,is_active=True).exists():
            return ServiceResult(
                success = False,
                message = "An account with this email already exists."
            )
        user = User.objects.filter(email=email,is_active=False).first()
        if user:
            if user.name != name:
                user.name = name
                user.save(update_fields=["name"])
            OTPService.send_otp(user.email,purpose,ip)
            return ServiceResult(
                success = True,
                message = f"An OTP is send to {email}" ,
                user = user
            )
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    name=name,
                    is_active=False,
                )
            OTPService.send_otp(user.email, purpose,ip)
            return ServiceResult(
                success = True,
                message = f"An OTP is send to {email}" ,
                user = user
            )
        except IntegrityError:
            return ServiceResult(
                success = False,
                message = "An account with this email already exists."
            )