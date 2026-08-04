import secrets
from accounts.models import User
from accounts.constants import OTPPurpose
from accounts.tasks import send_email_task
from accounts.caches.otp_caches import OTPCache

from .email_services import EmailService
from .service_result import ServiceResult


class OTPService:
    """
    OTP Service.
    """
    @staticmethod
    def generate_otp():
        return "".join(str(secrets.randbelow(10)) for i in range(6))
    
    @classmethod
    def send_otp(cls,email,purpose,ip):
        otp = cls.generate_otp()
        if not OTPCache.retrieve_ip_cooldown_expiry(ip):
            OTPCache.store_ip_cooldown(ip)
        count = OTPCache.increment_ip_otp_request_count(ip)
        if count >= OTPCache.MAX_OTP_REQUESTS_PER_IP:
            OTPCache.store_ip_block(ip)
        OTPCache.remove_otp(email,purpose)
        OTPCache.store_otp(email,purpose,otp)
        OTPCache.remove_otp_cooldown(ip,email)
        OTPCache.store_otp_cooldown(ip,email)
        if purpose == OTPPurpose.EMAIL_VERIFICATION:
            subject, text_message, html_message = EmailService.email_verification_email(otp)

        elif purpose == OTPPurpose.EMAIL_CHANGE:
            subject, text_message, html_message = EmailService.email_change_email(otp)

        else:
            raise ValueError(
                f"Unsupported OTP purpose: {purpose}"
            )
        send_email_task.delay(subject,text_message,html_message,email)

    
    @classmethod
    def resend_otp(cls,email,purpose,ip):
        ip_cooldown = OTPCache.retrieve_ip_cooldown_expiry(ip)
        ip_blocked = OTPCache.retrieve_ip_block(ip)
        ip_blocked_times = OTPCache.get_remaining_ip_cooldown_seconds(ip)
        ip_blocked_minutes = ip_blocked_times // 60
        ip_blocked_seconds = ip_blocked_times % 60
        if not ip_cooldown:
            OTPCache.remove_ip_block(ip)
        if ip_blocked:
            return ServiceResult(
                success=False,
                message=f"Please wait {ip_blocked_minutes}m {ip_blocked_seconds}s and try again due to maximum otp limits."
            )
        blocked = OTPCache.retrieve_otp_verification_block(ip,email)
        blocked_time = OTPCache.get_remaining_otp_verification_block_seconds(ip,email)
        blocked_minutes = blocked_time // 60
        blocked_seconds = blocked_time % 60
        if blocked:
            return ServiceResult(
                success=False,
                message=f"Please wait {blocked_minutes}m {blocked_seconds}s and try again."
            )
        cooldown = OTPCache.retrieve_otp_cooldown_expiry(ip,email)
        cooldown_time = OTPCache.get_remaining_otp_cooldown_seconds(ip,email)
        cooldown_minutes = cooldown_time  // 60
        cooldown_seconds = cooldown_time % 60
        if cooldown:
            return ServiceResult(
                success=False,
                message=f"Please wait {cooldown_minutes}m {cooldown_seconds}s and try again."
            )
        cls.send_otp(email,purpose,ip)
        return ServiceResult(
            success=True,
            message=f"An Email is send to {email}"
        )

    @staticmethod
    def verify_otp(email,purpose,entered_otp,ip):
        otp = OTPCache.retrieve_otp(email,purpose)
        blocked = OTPCache.retrieve_otp_verification_block(ip,email)
        blocked_time = OTPCache.get_remaining_otp_verification_block_seconds(ip,email)
        blocked_minutes = blocked_time  // 60
        blocked_seconds = blocked_time % 60
        if blocked:
            return ServiceResult(
                success=False,
                message=f"Please wait {blocked_minutes}m {blocked_seconds}s and try again."
            )
        if not otp:
            return ServiceResult(
                success=False,
                message="OTP is expired"
            )
        if otp == entered_otp and purpose == OTPPurpose.EMAIL_VERIFICATION:
            user = User.objects.filter(email=email).first()
            user.is_active = True
            user.save(update_fields=["is_active"])
            OTPCache.clear_user_otp_cache(ip,email,purpose)
            return ServiceResult(
                success = True,
                message = "Verification Done"
            )
        if otp == entered_otp and purpose == OTPPurpose.EMAIL_CHANGE:
            OTPCache.clear_user_otp_cache(ip,email,purpose)
            return ServiceResult(
                success = True,
                message = "Verification Done"
            )
        attempts = OTPCache.increment_otp_verification_attempts(ip,email)
        if attempts >= OTPCache.MAX_OTP_VERIFICATION_ATTEMPTS:
            OTPCache.store_otp_verification_block(ip,email)
            OTPCache.remove_otp_verification_attempts(ip,email)
            return ServiceResult(
            success = False,
            message = f"Maximun attempts reaches"
        )
        return ServiceResult(
            success = False,
            message = f"Invalid OTP {OTPCache.MAX_OTP_VERIFICATION_ATTEMPTS - attempts} attempts left's"
        )