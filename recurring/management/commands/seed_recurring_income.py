from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from recurring.models import (
    RecurringTransaction,
    TransactionType,
    Frequency,
)
from expense.models import ExpenseCategory, PaymentMethod

User = get_user_model()


class Command(BaseCommand):
    help = "Seed recurring expense transactions."

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
                self.style.ERROR(
                    f"User with email '{email}' does not exist."
                )
            )
            return

        today = timezone.localdate()

        recurring_expenses = [
            # Daily
            {
                "title": "Daily Food Expense",
                "amount": Decimal("1000.00"),
                "category": ExpenseCategory.FOOD,
                "payment_method": PaymentMethod.CASH,
                "frequency": Frequency.DAILY,
            },
            {
                "title": "Daily Transport Expense",
                "amount": Decimal("200.00"),
                "category": ExpenseCategory.TRANSPORT,
                "payment_method": PaymentMethod.CASH,
                "frequency": Frequency.DAILY,
            },

            # Monthly
            {
                "title": "Monthly Shopping",
                "amount": Decimal("10000.00"),
                "category": ExpenseCategory.SHOPPING,
                "payment_method": PaymentMethod.DEBIT_CARD,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Bills",
                "amount": Decimal("10000.00"),
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.BANK_TRANSFER,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Entertainment",
                "amount": Decimal("3000.00"),
                "category": ExpenseCategory.ENTERTAINMENT,
                "payment_method": PaymentMethod.DEBIT_CARD,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Health",
                "amount": Decimal("2500.00"),
                "category": ExpenseCategory.HEALTH,
                "payment_method": PaymentMethod.DEBIT_CARD,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Education",
                "amount": Decimal("5000.00"),
                "category": ExpenseCategory.EDUCATION,
                "payment_method": PaymentMethod.BANK_TRANSFER,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Travel",
                "amount": Decimal("4000.00"),
                "category": ExpenseCategory.TRAVEL,
                "payment_method": PaymentMethod.CREDIT_CARD,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Mobile Recharge",
                "amount": Decimal("1000.00"),
                "category": ExpenseCategory.MOBILE,
                "payment_method": PaymentMethod.JAZZCASH,
                "frequency": Frequency.MONTHLY,
            },
            {
                "title": "Monthly Software Subscription",
                "amount": Decimal("1500.00"),
                "category": ExpenseCategory.SOFTWARE,
                "payment_method": PaymentMethod.DEBIT_CARD,
                "frequency": Frequency.MONTHLY,
            },

            # Weekly
            {
                "title": "Weekly Other Expense",
                "amount": Decimal("1000.00"),
                "category": ExpenseCategory.OTHER,
                "payment_method": PaymentMethod.CASH,
                "frequency": Frequency.WEEKLY,
            },
        ]

        created = 0
        skipped = 0

        for item in recurring_expenses:
            _, was_created = RecurringTransaction.objects.get_or_create(
                user=user,
                title=item["title"],
                transaction_type=TransactionType.EXPENSE,
                frequency=item["frequency"],
                defaults={
                    "amount": item["amount"],
                    "expense_category": item["category"],
                    "payment_method": item["payment_method"],
                    "start_date": today,
                    "next_run": today,
                    "note": item["title"],
                    "is_active": True,
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