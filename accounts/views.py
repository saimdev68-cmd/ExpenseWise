from .forms import RegisterForm , LoginForm , OTPVerificationForm , CustomPasswordForm , EmailForm , CustomPasswordResetForm , CustomPasswordChangeForm , NameForm
from .mixins import OtpMixin , LoginMixin , PasswordResetdoneMixin , PasswordResetCompleteMixin
from django.shortcuts import render , redirect
from django.urls import reverse_lazy
from django.views import View , generic
from django.contrib import messages
from django.contrib.auth import  login , logout 
from django.contrib.auth.views import PasswordResetView , PasswordResetDoneView , PasswordResetConfirmView , PasswordResetCompleteView , PasswordChangeView , PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.register_service import RegisterService
from .services.otp_services import OTPService
from django.views.generic import CreateView , FormView
from .constants import OTPPurpose
from .utils import get_client_id
from .services.login_services import LoginService
from .sessions.pending_user_sessions import PendingUserSession
from django.http import JsonResponse
from django.urls import reverse
from .services.email_change_service import EmailChangeService
from django.contrib.auth import update_session_auth_hash

# Create your views here.


class SignUpView(LoginMixin, CreateView):
    template_name = "signup.html"
    form_class = RegisterForm

    def form_valid(self, form):
        ip = get_client_id(self.request)
        result = RegisterService.register_user(form.cleaned_data, OTPPurpose.EMAIL_VERIFICATION, ip)
        
        if result.success:
            messages.success(self.request, result.message)
            PendingUserSession.store(self.request, result.user)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": reverse("otp_verify")})
            return redirect("otp_verify")
            
        form.add_error(None, result.message)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
            
        return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)
    
class OtpVerifyView(LoginMixin, OtpMixin, FormView):
    template_name = "otp_verify.html"
    form_class = OTPVerificationForm

    def form_valid(self, form):
        ip = get_client_id(self.request)
        otp = form.cleaned_data.get("otp")
        user = self.get_pending_user()
        result = OTPService.verify_otp(user.email, OTPPurpose.EMAIL_VERIFICATION, otp, ip)
        
        if result.success:
            messages.success(self.request, result.message)
            login(self.request, user)
            PendingUserSession.clear(self.request)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": reverse("dashboard")})
            return redirect("dashboard")
            
        form.add_error(None, result.message)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
            
        return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)

class ResendOtpView(LoginMixin, OtpMixin, View):
    def post(self, request):
        user = self.get_pending_user()
        ip = get_client_id(request)
        result = OTPService.resend_otp(user.email, OTPPurpose.EMAIL_VERIFICATION, ip)
        
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if result.success:
            messages.success(request, result.message)
            if is_ajax:
                return JsonResponse({"success": True, "message": result.message})
            return redirect("otp_verify")
            
        messages.error(request, result.message)
        if is_ajax:
            return JsonResponse({"success": False, "message": result.message}, status=400)
        return redirect("otp_verify")
    
class LoginView(LoginMixin, FormView):
    template_name = "login.html"
    form_class = LoginForm
    
    def form_valid(self, form):
        result = LoginService.check_user(form.cleaned_data, self.request)
        
        if result.success:
            messages.success(self.request, result.message)
            login(self.request, result.user)
            
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "redirect_url": reverse("dashboard")})
            return redirect("dashboard")
            
        form.add_error(None, result.message)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
            
        return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)

class LogoutView(View):
    def post(self,request):
        logout(request)
        messages.success(request,"Logout Successfully")
        return redirect ("login")
    

class PasswordresetView(LoginMixin, PasswordResetView):
    template_name = "password_reset.html"
    form_class = CustomPasswordResetForm

    email_template_name = "password_reset_email.txt"
    subject_template_name = "password_reset_subject.txt"

    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        # Send password reset email
        response = super().form_valid(form)

        # Mark session
        self.request.session["password_reset_done"] = True

        # AJAX request
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "redirect_url": reverse("password_reset_done"),
            })

        # Normal request
        return response

    def form_invalid(self, form):

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "errors": form.errors.get_json_data(),
                },
                status=400,
            )

        return super().form_invalid(form)
    

class PasswordresetdoneView(LoginMixin,PasswordResetdoneMixin,PasswordResetDoneView):
    template_name = "password_reset_done.html"
    

class PasswordresetconfirmView(LoginMixin, PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    form_class = CustomPasswordForm
    success_url = reverse_lazy("password_reset_complete")

    def form_valid(self, form):
        self.request.session["password_reset_confirm"] = True
        response = super().form_valid(form)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True, "redirect_url": str(self.success_url)})
            
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)

class PasswordresetCompleteView(LoginMixin,PasswordResetCompleteMixin,PasswordResetCompleteView):
    template_name = "password_reset_complete.html"
    
class UserDetailView(LoginRequiredMixin,generic.DetailView):
    template_name = "user_detail.html"
    context_object_name = "user"

    def get_object(self, queryset = None):
        return self.request.user
    
class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "user_update.html"
    form_class = NameForm
    success_url = reverse_lazy("user_detail")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": True,
                "redirect_url": str(self.success_url)
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": False,
                "errors": form.errors
            }, status=400)
        return super().form_invalid(form)
    

class EmailUpdateView(LoginRequiredMixin, View):
    template_name = "email_update.html"

    def get(self, request):
        form = EmailForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EmailForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if not form.is_valid():
            if is_ajax:
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            return render(request, self.template_name, {"form": form})
        
        new_email = form.cleaned_data.get('email')

        result = EmailChangeService.request_email_change(
            user=request.user,
            new_email=new_email,
            ip=get_client_id(request),
        )

        if not result.success:
            form.add_error("email", result.message)
            if is_ajax:
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            return render(request, self.template_name, {"form": form})

        request.session["email_update"] = True
        messages.success(request, result.message)
        
        success_url = reverse("email_otp_verify")
        if is_ajax:
            return JsonResponse({
                "success": True, 
                "redirect_url": success_url
            })
        return redirect(success_url)


class EmailOtpVerifyView(LoginRequiredMixin, generic.FormView):
    template_name = "email_otp_verify.html"
    form_class = OTPVerificationForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("email_update"):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "redirect_url": reverse("email_update")}, status=400)
            return redirect("email_update")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        otp = form.cleaned_data["otp"]
        user = self.request.user
        is_ajax = self.request.headers.get('x-requested-with') == 'XMLHttpRequest'

        pending_email = getattr(user, "pending_email_change", None)
        if not pending_email:
            form.add_error(None, "No pending email change request found.")
            if is_ajax:
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            return self.form_invalid(form)

        ip = get_client_id(self.request)

        result = OTPService.verify_otp(
            email=pending_email.email,
            purpose=OTPPurpose.EMAIL_CHANGE,
            entered_otp=otp,
            ip=ip,
        )

        if not result.success:
            form.add_error(None, result.message)
            if is_ajax:
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            return self.form_invalid(form)

        self.request.session.pop("email_update", None)
        user.email = pending_email.email
        user.save(update_fields=['email'])
        pending_email.delete()
        
        messages.success(
            self.request,
            "OTP verified successfully. Email is updated successfully."
        )

        success_url = reverse("user_detail")
        if is_ajax:
            return JsonResponse({"success": True, "redirect_url": success_url})
        return redirect(success_url)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return super().form_invalid(form)

class EmailResendOtpView(LoginRequiredMixin, View):

    def post(self, request):
        user = request.user
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        pending_email = getattr(user, "pending_email_change", None)

        if not pending_email:
            msg = "No pending email change request found."
            redirect_url = reverse("email_update")
            
            if is_ajax:
                return JsonResponse({
                    "success": False, 
                    "message": msg, 
                    "redirect_url": redirect_url
                }, status=400)
            
            messages.error(request, msg)
            return redirect(redirect_url)

        ip = get_client_id(request)

        result = OTPService.resend_otp(
            email=pending_email.email,
            purpose=OTPPurpose.EMAIL_CHANGE,
            ip=ip,
        )

        success_url = reverse("email_otp_verify")

        if not result.success:
            if is_ajax:
                return JsonResponse({
                    "success": False, 
                    "message": result.message
                }, status=400)
            
            messages.error(request, result.message)
            return redirect(success_url)

        if is_ajax:
            return JsonResponse({
                "success": True, 
                "message": result.message, 
                "redirect_url": success_url
            })

        messages.success(request, result.message)
        return redirect(success_url)
    
class PasswordchangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "password_change.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("password_change_done")

    def form_valid(self, form):
        self.request.session["password_change_done"] = True
        self.object = form.save()
        update_session_auth_hash(self.request, self.object)
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": True,
                "redirect_url": str(self.success_url)
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": False,
                "errors": form.errors
            }, status=400)
        return super().form_invalid(form)

class PasswordchangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "password_change_done.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("password_change_done"):
            return redirect("password_change")
        request.session.pop("password_change_done", None)
        return super().dispatch(request, *args, **kwargs)