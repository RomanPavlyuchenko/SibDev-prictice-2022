import django_filters

from ...models.transaction import Transaction


class TransactionFilter(django_filters.FilterSet):

    transaction_month = django_filters.DateFilter(field_name='transaction_date',
                                                  method='month_filter')
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

    def month_filter(self, queryset, name, value):
        return queryset.filter(
            transaction_type='expense'
        ).filter(
            **{"%s__year" % name: value.year, "%s__month" % name: value.month}
        )

    class Meta:
        model = Transaction
        fields = [
            'transaction_date',
        ]
