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
