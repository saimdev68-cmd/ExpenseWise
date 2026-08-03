from django import forms
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm , SetPasswordForm , PasswordResetForm , PasswordChangeForm

from .models import User
from .tasks import send_email_task


class RegisterForm(UserCreationForm):
    """
    User Registration Form.
    """
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
            "placeholder": "Create a password",
            "autocomplete": "new-password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Re-enter password",
            "autocomplete": "new-password",
        })
    
    
class LoginForm(forms.Form):
    """
    User Login Form.
    """
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
    """
    User OTP Verification Form.
    """
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
    """
    User Forget Password Email Form.
    """

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

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = render_to_string(
            subject_template_name,
            context,
        ).strip()

        text_message = render_to_string(
            email_template_name,
            context,
        )

        html_message = None
        if html_email_template_name:
            html_message = render_to_string(
                html_email_template_name,
                context,
            )

        send_email_task.delay(
            subject,
            text_message,
            html_message,
            to_email,
        )
    
class CustomPasswordForm(SetPasswordForm):
    """
    Set New Password Form.
    """
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
    """
    Set New Password Form.
    """
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
    """
    User Change Email Form.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your new email",
            'label':  "Email Address",
            "autocomplete": "email",
        })
    )
    
class NameForm(forms.ModelForm):
    """
    User Name Edit Form.
    """
    class Meta:
        model = User
        fields = ["name"]
        labels = {
            "name": "Full Name"
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full name",
                    "autocomplete": "name",
                }
            ),
        }