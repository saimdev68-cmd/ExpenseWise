from . import views
from django.urls import path


urlpatterns = [
    path("signup/",views.SignUpView.as_view(),name="signup"),
    path("otp-verify/",views.OtpVerifyView.as_view(),name="otp_verify"),
    path("login/",views.LoginView.as_view(),name="login"),
    path("logout/",views.LogoutView.as_view(),name="logout"),
    path("resend-otp/",views.ResendOtpView.as_view(),name="resend_otp"),
    path("password-reset/",views.PasswordresetView.as_view(),name="password_reset"),
    path("password-reset/done/",views.PasswordresetdoneView.as_view(),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',views.PasswordresetconfirmView.as_view(),name='password_reset_confirm'),
    path("reset/done/",views.PasswordresetCompleteView.as_view(),name="password_reset_complete"),
    path("email-update/",views.EmailUpdateView.as_view(),name="email_update"),
    path("email/otp-verify/",views.EmailOtpVerifyView.as_view(),name="email_otp_verify"),
    path("email/resend-otp/",views.EmailResendOtpView.as_view(),name="email_resend_otp"),
    path("password/change/",views.PasswordchangeView.as_view(),name="password_change"),
    path('password/change/done/',views.PasswordchangeDoneView.as_view(),name="password_change_done"),
    path("user_detail/",views.UserDetailView.as_view(),name="user_detail"),
    path("user_update/",views.UserUpdateView.as_view(),name="user_update"),
]