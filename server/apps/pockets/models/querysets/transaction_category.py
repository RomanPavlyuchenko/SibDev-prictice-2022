from typing import List
from decimal import Decimal

from django.db.models import QuerySet, Sum, DecimalField
from django.db.models.functions import Coalesce


class TransactionCategoryQuerySet(QuerySet):
    def annotate_with_transaction_sums(self):
        """
        :return: TransactionCategoryQuerySet
        """

        return self.annotate(
            transactions_sum=Coalesce(
                Sum('transactions__amount', distinct=True),
                0,
                output_field=DecimalField(),
            ),
        ).order_by('-transactions_sum')

    def get_list_top_categories(self) -> List[dict[str, Decimal]]:
        top_rank = 3
        top_categories = list()
        queryset = self.annotate_with_transaction_sums()

        if queryset.count() > top_rank:
            top_categories.extend(
                queryset.values()[:top_rank])

            top_categories.append(
                {'name': 'Другие',
                 'transactions_sum':
                     queryset[top_rank:].aggregate(
                         sum=Coalesce(
                             Sum('transactions_sum'),
                             0,
                             output_field=DecimalField(),
                         ),
                     )['sum']
                 }
            )
        else:
            top_categories.extend(queryset)

        return top_categories
