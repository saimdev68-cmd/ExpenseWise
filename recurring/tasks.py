from django.utils import timezone
from django.db import transaction
from celery import shared_task

from .models import RecurringTransaction


@shared_task(bind=True,autoretry_for=(Exception,),retry_backoff=True,retry_kwargs={"max_retries": 3})
def process_recurring_transactions(self):
    today = timezone.localdate()

    recurring_transactions = RecurringTransaction.objects.select_for_update().filter(is_active=True,next_run__lte=today).order_by("next_run")

    processed = 0
    skipped = 0
    failed = 0

    for recurring in recurring_transactions:

        try:
            with transaction.atomic():
                recurring = RecurringTransaction.objects.select_for_update().get(pk=recurring.pk)

                if not recurring.is_active:
                    skipped += 1
                    continue

                if recurring.is_finished():
                    recurring.is_active = False
                    recurring.save(update_fields=["is_active","updated_at"])
                    skipped += 1
                    continue

                if not recurring.can_run():
                    skipped += 1
                    continue

                result = recurring.run_now()

                if result is None:
                    skipped += 1
                else:
                    processed += 1

        except Exception:
            failed += 1
            raise

    return {"processed": processed,"skipped": skipped,"failed": failed,"processed_at": str(today)}