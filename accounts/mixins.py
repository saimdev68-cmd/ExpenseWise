import random
from .tasks import send_otp_mail , send_email_otp_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect , get_object_or_404
from .models import User
from .sessions.pending_user_sessions import PendingUserSession

class LoginMixin:    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect ("dashboard")
        return super().dispatch(request, *args, **kwargs)
    
class PasswordResetdoneMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_reset_done"):
            return redirect ("password_reset")
        request.session.pop("password_reset_done",None)
        return super().dispatch(request, *args, **kwargs)
    
class PasswordResetCompleteMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_reset_confirm"):
            return redirect ("login")
        request.session.pop("password_reset_confirm",None)
        return super().dispatch(request, *args, **kwargs)


class OtpMixin:
    def get_pending_user(self):
        return get_object_or_404(
            User,
            id=PendingUserSession.get_user_id(self.request)
        )
    
    def dispatch(self, request, *args, **kwargs):
        if not PendingUserSession.get_user_id(request):
            return redirect ("signup")
        return super().dispatch(request, *args, **kwargs)

    
class EmailOtpMixin:
    def send_or_resend_email_otp(self,user):
        otp = str(random.randint(100000,999999))
        print(otp)
        user.otp = make_password(otp)
        user.otp_created_at = timezone.now()
        user.otp_block_time = None
        user.otp_attempt = 0
        user.save()
        send_email_otp_mail.delay(user.pending_email,otp)
        return otp