from django.db import models
from django.db.models import QuerySet, Sum, DecimalField, ExpressionWrapper, F
from django.db.models.functions import Coalesce


class TargetQuerySet(QuerySet):
    def annotate_with_transaction_sums(self):
        return self.annotate(
            transactions_sum=Coalesce(
                Sum('balances__amount', distinct=True),
                0,
                output_field=DecimalField(),
            ),
        )

    def aggregate_total(self, *args, **kwargs):
        return self.aggregate(
            total=Coalesce(
                Sum('balances__amount'),
                0,
                output_field=DecimalField(),
            )
        )

    def annotate_deadline(self):
        return self.annotate(
            deadline=ExpressionWrapper(
                F('create_date') + Coalesce('target_term', 0) * 30,
                output_field=models.DateField())
        )
