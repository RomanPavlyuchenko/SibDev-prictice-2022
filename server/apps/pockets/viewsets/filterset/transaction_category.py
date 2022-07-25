import django_filters

from ...models.transaction_category import TransactionCategory


class TransactionCategoryFilter(django_filters.FilterSet):

    transaction_year = django_filters.NumberFilter(
        field_name='transactions__transaction_date',
        lookup_expr='year'
    )
    transaction_month = django_filters.NumberFilter(
        field_name='transactions__transaction_date',
        lookup_expr='month'
    )

    order = django_filters.OrderingFilter(
        fields=(
            ('transactions_sum', 'amount'),
        ),
        field_labels={
            'amount': 'Category amount',
        }
    )

    class Meta:
        model = TransactionCategory
        fields = ('transactions',)
