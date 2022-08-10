from decimal import Decimal

from django.db.models import QuerySet, Sum

from ....pockets.constants import TransactionTypes
from ....pockets.models import Transaction


class TargetBalanceQuerySet(QuerySet):
    def aggregate_balance(self, *args, **kwargs) -> dict[str, Decimal]:
        return self.aggregate(
            total=Sum('amount',),
            )

    def create(self, **kwargs):
        Transaction.objects.create(
            category_id=kwargs.pop('category_id'),
            user=kwargs.pop('user'),
            transaction_type=TransactionTypes.EXPENSE,
            amount=kwargs['amount'],
        )
        return super().create(**kwargs)
