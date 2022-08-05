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

    def aggregate_analytics(self, *args, **kwargs):
        analytics = dict()
        queryset_open_targets = self.filter(is_closed=False)
        queryset_percent = self.filter(balances__is_percent=True)
        category_top = self.values('category').annotate(
            count=Count('category')
        ).order_by('-count').first()
        category_closed_top = self.filter(is_closed=True).values('category').annotate(
            count=Count('category')
        ).order_by('-count').first()

        analytics.update(
            {
                'open_targets_count': queryset_open_targets.count(),
                'open_targets_amount': queryset_open_targets.aggregate_total()['total'],
                'fastest_finish': (
                        self.annotate_deadline(self).order_by('deadline').first().deadline - datetime.now().date()
                ).days,
                'percents_sum': queryset_percent.aggregate_total()['total'],
                'category_top': None if category_top is None else category_top['category'],
                'category_closed_top': None if category_closed_top is None else category_closed_top['category'],

            }
        )
        queryset_percent = self.filter(
            balances__is_percent=True,
            balances__transaction_date__year=datetime.now().year,
            balances__transaction_date__month=datetime.now().month,
        )
        analytics.update(
            {
                'percents_sum_current_month': queryset_percent.aggregate_total()['total']
            }
        )

        return analytics
