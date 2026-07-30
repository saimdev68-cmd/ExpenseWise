from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from expense.models import Expense, ExpenseCategory, PaymentMethod

User = get_user_model()


class Command(BaseCommand):
    help = "Seed monthly miscellaneous expenses from January 2025 to July 2026."

    EXPENSES = [
        {
            "title": "Entertainment",
            "category": ExpenseCategory.ENTERTAINMENT,
            "amount": 3000,
            "payment_method": PaymentMethod.DEBIT_CARD,
        },
        {
            "title": "Health",
            "category": ExpenseCategory.HEALTH,
            "amount": 2500,
            "payment_method": PaymentMethod.DEBIT_CARD,
        },
        {
            "title": "Education",
            "category": ExpenseCategory.EDUCATION,
            "amount": 5000,
            "payment_method": PaymentMethod.BANK_TRANSFER,
        },
        {
            "title": "Travel",
            "category": ExpenseCategory.TRAVEL,
            "amount": 4000,
            "payment_method": PaymentMethod.CREDIT_CARD,
        },
        {
            "title": "Mobile Recharge",
            "category": ExpenseCategory.MOBILE,
            "amount": 1000,
            "payment_method": PaymentMethod.JAZZCASH,
        },
        {
            "title": "Software Subscription",
            "category": ExpenseCategory.SOFTWARE,
            "amount": 1500,
            "payment_method": PaymentMethod.DEBIT_CARD,
        },
        {
            "title": "Other Expense",
            "category": ExpenseCategory.OTHER,
            "amount": 2000,
            "payment_method": PaymentMethod.CASH,
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            required=True,
            help="Email address of the user.",
        )

    def handle(self, *args, **options):
        email = options["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with email '{email}' does not exist.")
            )
            return

        created = 0
        skipped = 0

        for year in (2025, 2026):
            end_month = 12 if year == 2025 else 7

            for month in range(1, end_month + 1):
                expense_date = date(year, month, 1)

                for expense in self.EXPENSES:
                    _, was_created = Expense.objects.get_or_create(
                        user=user,
                        title=expense["title"],
                        category=expense["category"],
                        payment_method=expense["payment_method"],
                        date=expense_date,
                        defaults={
                            "amount": expense["amount"],
                            "note": f'{expense["title"]} for {expense_date:%B %Y}',
                            "is_recurring": False,
                        },
                    )

                    if was_created:
                        created += 1
                    else:
                        skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created: {created}, Skipped: {skipped}"
            )
        )