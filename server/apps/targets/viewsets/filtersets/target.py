import django_filters


class TargetFilter(django_filters.FilterSet):
    order = django_filters.OrderingFilter(
        fields=(
            ('deadline', 'deadline'),
            ('create_date', 'created'),
            ('percent', 'percent'),
            ('transactions_sum', 'sum')
        )
    )
