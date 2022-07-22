from decimal import Decimal

from django.db.models import QuerySet, Sum, DecimalField
from django.db.models.functions import Coalesce


class TargetBalanceQuerySet(QuerySet):
    def aggregate_balance(self, *args, **kwargs) -> dict[str, Decimal]:
        total = self.aggregate(
            total=Sum('amount',),
            )

        return total

    def annotate_with_transaction_sums(self):
        return self.annotate(
            transactions_sum=Coalesce(
                Sum('transactions__amount', distinct=True),
                0,
                output_field=DecimalField(),
            ),
        ).order_by('-transactions_sum')
