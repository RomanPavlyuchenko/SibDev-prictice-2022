import django_filters

from ...models.transaction import TransactionTypes
from ...models.transaction_category import TransactionCategory


class TransactionCategoryFilter(django_filters.FilterSet):

    transaction_month = django_filters.DateFilter(field_name='transactions__transaction_date',
                                                  method='month_filter')
    order = django_filters.OrderingFilter(
        fields=(
            ('transactions_sum', 'amount'),
        ),
        field_labels={
            'amount': 'Category amount',
        }
    )

    def month_filter(self, queryset, name, value):
        return queryset.filter(
            transactions__transaction_type=TransactionTypes.EXPENSE,
            **{
                "%s__year" % name: value.year,
                "%s__month" % name: value.month
            },
        )

    class Meta:
        model = TransactionCategory
        fields = [
            'transactions__transaction_date',
        ]
