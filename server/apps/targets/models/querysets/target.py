from datetime import datetime

from django.db import models
from django.db.models import QuerySet, Sum, DecimalField, ExpressionWrapper, F, Count
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

    def annotate_deadline(self, *args, **kwargs):
        return self.annotate(
            deadline=ExpressionWrapper(
                F('create_date') + Coalesce('target_term', 0) * 30,
                output_field=models.DateField()
            )
        )

    def annotate_daily_percent(self, *args, **kwargs):
        queryset = self.annotate_with_transaction_sums()
        return queryset.annotate(
            daily_percent=ExpressionWrapper(
                F('transactions_sum') * F('percent') / (365 * 100),
                output_field=models.DecimalField(),
            )
        )

    def annotate_finish_days(self, *args, **kwargs):
        return self.annotate_deadline().annotate(
            finish_days=ExpressionWrapper(
                (F('deadline') - datetime.now().date()),
                output_field=models.DurationField(),
            )
        ).order_by('finish_days')

    def get_top_category_name_or_none(self, *args, **kwargs):
        top_category = self.values('category', 'category__name').annotate(
            count=Count('category')
        ).order_by('-count').first()
        return None if top_category is None else top_category['category__name']
