import django_filters

from ...models.transaction import Transaction


class TransactionFilter(django_filters.FilterSet):

    transaction_year = django_filters.NumberFilter(
        field_name='transaction_date',
        lookup_expr='year'
    )
    transaction_month = django_filters.NumberFilter(
        field_name='transaction_date',
        lookup_expr='month'
    )
    order = django_filters.OrderingFilter(
        fields=(
            ('category', 'category'),
            ('transaction_date', 'date'),
            ('amount', 'amount'),
        ),
        field_labels={
            'category': 'Transaction category',
            'transaction_date': 'Transaction date',
            'amount': 'Transaction amount',
        }
    )

    class Meta:
        model = Transaction
        fields = ('transaction_date',)
