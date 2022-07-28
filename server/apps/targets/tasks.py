from .celery.celery import app
import logging
from .constants import TargetBalanceTypes
from .models import Target, TargetBalance


@app.task()
def accrual_interest():
    queryset = Target.objects.get_queryset().filter(
        is_closed=False
    ).prefetch_related(
        'balances'
    ).annotate_with_transaction_sums()
    balances = []
    for target in queryset:
        percent_per_day = round(target.transactions_sum / 100 * (target.percent / 365), 2)
        if percent_per_day > 0:
            balances.append(
                TargetBalance(
                    amount=percent_per_day,
                    target_id=target.id,
                    plenishment_method=TargetBalanceTypes.PERCENT
                )
            )
    TargetBalance.objects.bulk_create(balances)
    logging.info(f'interest was accrued for {len(balances)} targets')
