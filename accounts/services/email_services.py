from django.template.loader import render_to_string

class EmailService:
    """
    Email Service
    """
    @staticmethod
    def email_verification_email(otp):
        subject = "Verify Your Email - ExpenseWise"

        context = {
            "otp": otp,
        }

        html_message = render_to_string(
            "emails/email_verification.html",
            context,
        )

        plain_message = render_to_string(
            "emails/email_verification.txt",
            context,
        )

        return subject, plain_message, html_message

    @staticmethod
    def email_change_email(otp):
        subject = "Verify Your New Email - ExpenseWise"

        context = {
            "otp": otp,
        }

        html_message = render_to_string(
            "emails/email_change.html",
            context,
        )

        plain_message = render_to_string(
            "emails/email_change.txt",
            context,
        )

        return subject, plain_message, html_message