from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from budgets.models import Budget
from expense.models import ExpenseCategory

User = get_user_model()


class Command(BaseCommand):
    help = "Seed monthly budgets from January 2025 to July 2026."

    BUDGETS = {
        ExpenseCategory.FOOD: 25000,
        ExpenseCategory.TRANSPORT: 10000,
        ExpenseCategory.SHOPPING: 10000,
        ExpenseCategory.BILLS: 10000,
        ExpenseCategory.ENTERTAINMENT: 10000,
        ExpenseCategory.HEALTH: 10000,
        ExpenseCategory.EDUCATION: 10000,
        ExpenseCategory.TRAVEL: 10000,
        ExpenseCategory.MOBILE: 10000,
        ExpenseCategory.SOFTWARE: 10000,
        ExpenseCategory.OTHER: 10000,
    }

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

        created = 0
        skipped = 0

        for year in (2025, 2026):
            end_month = 12 if year == 2025 else 7

            for month in range(1, end_month + 1):
                for category, amount in self.BUDGETS.items():
                    _, was_created = Budget.objects.get_or_create(
                        user=user,
                        category=category,
                        month=month,
                        year=year,
                        defaults={
                            "amount": amount,
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