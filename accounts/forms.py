from django import forms
from .models import User
from .tasks import send_password_reset_mail
from django.contrib.auth.forms import UserCreationForm , SetPasswordForm , PasswordResetForm , PasswordChangeForm
from django.template.loader import render_to_string

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "name", "password1", "password2"]
        labels = {
            "email": "Email Address",
            "name": "Full Name",
            "password1": "Password",
            "password2": "Confirm Password",
        }
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email address",
                    "autocomplete": "email",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full name",
                    "autocomplete": "name",
                }
            ),
        }

    def validate_unique(self):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Create a strong password",
            "autocomplete": "new-password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Re-enter your password",
            "autocomplete": "new-password",
        })
    
    
class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label="Verification Code",
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter the 6-digit verification code",
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "maxlength": "6",
            }
        ),
    )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )
    
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name = None):
        subject = render_to_string(subject_template_name,context).strip()
        message = render_to_string(email_template_name, context)
        send_password_reset_mail.delay(subject,message, from_email, [to_email])
    
class CustomPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Enter New Password"
            }
        ),
        help_text=""
    )
    new_password2 = forms.CharField(
        label="Comfirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Confirm New Password"
            }
        ),
        help_text=""
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Enter Old Password"
            }
        ),
        help_text=""
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Enter New Password"
            }
        ),
        help_text=""
    )
    new_password2 = forms.CharField(
        label="Comfirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Confirm New Password"
            }
        ),
        help_text=""
    )

class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your new email",
            "autocomplete": "email",
        })
    )
    
class EmailOtpForm(forms.Form):
    otp = forms.CharField(
        label="Otp verifcation",
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "class":"form-control",
                "placeholder":"Enter OTP"
            }
        )
    )

class NameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name"]