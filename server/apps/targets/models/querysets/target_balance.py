from decimal import Decimal

from django.db.models import QuerySet, Sum


class TargetBalanceQuerySet(QuerySet):
    def aggregate_balance(self, *args, **kwargs) -> dict[str, Decimal]:
        return self.aggregate(
            total=Sum('amount',),
            )
