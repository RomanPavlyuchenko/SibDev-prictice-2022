import django_filters


class TargetFilter(django_filters.FilterSet):
    order = django_filters.OrderingFilter(
        fields=(
            ('target_deadline', 'deadline'),
            ('create_date', 'created'),
            ('balance__percent', 'percent'),
            ('transactions_sum', 'sum')
        )
    )
