from django.shortcuts import redirect , get_object_or_404

from .models import User
from .sessions.pending_user_sessions import PendingUserSession


class LoginMixin:    
    """
    For Login User Mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect ("dashboard")
        return super().dispatch(request, *args, **kwargs)
    
class PasswordResetdoneMixin:
    """
    Password Reset Done Mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_reset_done"):
            return redirect ("password_reset")
        request.session.pop("password_reset_done",None)
        return super().dispatch(request, *args, **kwargs)
    
class PasswordResetCompleteMixin:
    """
    Password Reset Complete Mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_reset_confirm"):
            return redirect ("login")
        request.session.pop("password_reset_confirm",None)
        return super().dispatch(request, *args, **kwargs)

class PasswordChangeDoneMixin:
    """
    Password Reset Complete Done Mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_change_done"):
            return redirect("password_change")
        request.session.pop("password_change_done", None)
        return super().dispatch(request, *args, **kwargs)

class OtpMixin:
    """
    OTP Mixin.
    """
    def get_pending_user(self):
        return get_object_or_404(User,id=PendingUserSession.get_user_id(self.request))
    
    def dispatch(self, request, *args, **kwargs):
        if not PendingUserSession.get_user_id(request):
            return redirect ("signup")
        return super().dispatch(request, *args, **kwargs)
