from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action

from .filtersets import TargetFilter
from ..models import Target, TargetBalance
from ..models.querysets import TargetQuerySet
from ..serializers import (
    TargetCreateSerializer,
    TargetRetrieveSerializer,
    TargetBalanceCreateSerializer,
)
from ..serializers.target import TargetListSerializer
from ...pockets.constants import TransactionTypes
from ...pockets.models import Transaction


def percent_accrual():
    queryset = Target.objects.get_queryset().filter(
        is_closed=False
    ).prefetch_related(
        'balances'
    ).annotate_with_transaction_sums()
    balances = []
    for target in queryset:
        percent_per_day = target.transactions_sum / 100 * (target.percent / 365)
        if percent_per_day > 0:
            balances.append(
                TargetBalance(
                    amount=percent_per_day,
                    target_id=target.id,
                    is_percent=True
                )
            )
    TargetBalance.objects.bulk_create(balances)
    return balances


class TargetViewSet(viewsets.ModelViewSet):
    pagination_class = pagination.LimitOffsetPagination
    pagination_class.default_limit = 20
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TargetFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            serializer_class = TargetCreateSerializer
        elif self.action in ('list', 'retrieve', 'close_target'):
            serializer_class = TargetListSerializer
        else:
            serializer_class = TargetRetrieveSerializer
        return serializer_class

    def get_queryset(self) -> TargetQuerySet:
        queryset = Target.objects.filter(
            user=self.request.user,
        ).prefetch_related('balances').order_by(
            '-create_date',
        )
        if self.action in ('list', 'retrieve',):
            queryset = queryset.annotate_with_transaction_sums()
        if self.action in ('list', 'destroy',):
            queryset = queryset.annotate_deadline()
        return queryset

    def create(self, request, *args, **kwargs):
        target_serializer = self.get_serializer_class()(
            context={'request': request},
            data=request.data,
        )

        target_serializer.is_valid(raise_exception=True)
        target = target_serializer.save()

        if 'initial_payment' in request.data:
            target.balances.add(self._create_balance(request, target_id=target.id, *args, **kwargs))
            target.save()

        headers = self.get_success_headers(target_serializer.data)
        return Response(
            target_serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        total = self.get_queryset().filter(
            pk=kwargs['pk']
        ).aggregate_total()['total']

        if total >= instance.target_amount and not instance.is_closed:
            Transaction.objects.create(
                amount=total,
                category_id=instance.category.id,
                transaction_type=TransactionTypes.INCOME,
                user=request.user,
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST',), detail=True, url_path='top-up')
    def top_up(self, request, *args, **kwargs):
        instance = self.get_object()
        data = {
            'target': instance.id,
            'amount': request.data.get('amount', None),
            'transaction': {
                'category': instance.category.id,
                'amount': request.data.get('amount', None),
                'transaction_type': TransactionTypes.EXPENSE,
            }
        }
        balance_serializer = TargetBalanceCreateSerializer(
            context={'request': request},
            data=data
        )
        balance_serializer.is_valid(raise_exception=True)
        balance = balance_serializer.save()
        instance.balances.add(balance)
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    @action(methods=('GET',), detail=True, url_path='close')
    def close_target(self, request, *args, **kwargs):
        instance = self.get_object()
        total = self.get_queryset().filter(
            pk=kwargs['pk']
        ).aggregate_total()['total']
        if total < instance.target_amount or instance.is_closed:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Transaction.objects.create(
            amount=total,
            category_id=instance.category.id,
            transaction_type=TransactionTypes.INCOME,
            user=request.user,
        )
        instance.is_closed = True
        instance.closing_date = date.today()
        instance.save()
        return Response(
            TargetRetrieveSerializer(instance).data,
            status=status.HTTP_200_OK,
        )

    def _create_balance(self, request: Request, *args, **kwargs) -> TargetBalance:

        Transaction.objects.create(
            category_id=request.data.get('category', None),
            user=request.user,
            transaction_type=TransactionTypes.EXPENSE,
            amount=request.data.get('initial_payment', None),
        )
        balance = TargetBalance.objects.create(
            target_id=kwargs.get('target_id'),
            amount=request.data.get('initial_payment', None),
        )

        return balance
