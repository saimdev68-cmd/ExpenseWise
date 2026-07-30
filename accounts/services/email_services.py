class EmailService:

    @staticmethod
    def email_verification_email(otp):
        subject = "Verify Your Email - ExpenseWise"

        message = f"""
Hi,

Welcome to ExpenseWise!

Your email verification code is:

{otp}

This code is valid for 10 minutes.

If you did not create an ExpenseWise account, you can safely ignore this email.

Regards,
ExpenseWise Team
""".strip()

        return subject, message

    @staticmethod
    def email_change_email(otp):
        subject = "Verify Your New Email - ExpenseWise"

        message = f"""
Hi,

You requested to change your ExpenseWise email address.

Your email verification code is:

{otp}

This code is valid for 10 minutes.

If you did not request an email change, you can safely ignore this email.

Regards,
ExpenseWise Team
""".strip()

        return subject, message