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
        top_category_list = list()
        other_category = {
            'category_name': 'Other',
            'transactions_sum': Decimal()
                 }
        for i in range(self.values().count()):
            if i < top_rank:
                top_category_list.append(
                    {
                        'category_name': self.values()[i]['name'],
                        'transactions_sum': self.values()[i]['transactions_sum'],
                    }
                )
            else:
                other_category['transactions_sum'] += self.values()[i]['transactions_sum']
        if self.values().count() > top_rank:
            top_category_list.append(other_category)

        return top_category_list
