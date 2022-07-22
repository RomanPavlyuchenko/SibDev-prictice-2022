from decimal import Decimal

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filtersets import TargetFilter
from ..constants import TargetBalanceTotalException
from ..models import Target
from ..models.querysets import TargetBalanceQuerySet
from ..serializers import TargetCreateSerializer, TargetRetrieveSerializer, TargetBalanceSerializer, TargetSerializer
from ...pockets.constants import TransactionTypes
from ...pockets.models import Transaction
from ...pockets.serializers import TransactionCreateSerializer


class TargetViewSet(viewsets.ModelViewSet):
    pagination_class = pagination.LimitOffsetPagination
    pagination_class.default_limit = 20
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TargetFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'transactions'):
            serializer_class = TargetCreateSerializer
        elif self.action == 'retrieve':
            serializer_class = TargetSerializer
        else:
            serializer_class = TargetRetrieveSerializer
        return serializer_class

    def get_queryset(self) -> TargetBalanceQuerySet:
        queryset = Target.objects.filter(
            user=self.request.user,
        ).select_related('balance')
        if self.action == 'list':
            queryset = queryset.annotate_with_transaction_sums()
        return queryset

    def create(self, request, *args, **kwargs):
        target_serializer = self.get_serializer_class()(
            context={'request': request},
            data=request.data,
        )

        target_serializer.is_valid(raise_exception=True)
        target = target_serializer.save()

        if 'amount' in request.data:
            self._create_balance(request, target)

        headers = self.get_success_headers(target_serializer.data)
        return Response(
            target_serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.balance and 'amount' in request.data:
            self._create_balance(request, instance)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if timezone.now().date() < instance.target_deadline:
            total = instance.balance.transactions.get_queryset().aggregate_balance(is_abs=True)['balance']
            transaction_serializer = TransactionCreateSerializer(
                context={'request': request},
                data={
                    'transaction_type': TransactionTypes.INCOME,
                    'amount': total,
                },
            )
            transaction_serializer.is_valid(raise_exception=True)
            transaction = transaction_serializer.save()
            instance.balance.transactions.all().delete()
            instance.balance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST',), detail=True, url_path='transactions')
    def transactions(self, request: Request, pk=None, *args, **kwargs):
        instance = self.get_object()
        transaction_serializer = TransactionCreateSerializer(
            context={'request': request},
            data={'transaction_type': TransactionTypes.EXPENSE,
                  'amount': request.data['amount'],
                  'category': instance.category.id,
                  }
        )
        transaction_serializer.is_valid(raise_exception=True)
        transaction = transaction_serializer.save()
        transaction.balance = instance.balance
        transaction.save()
        headers = self.get_success_headers(transaction_serializer.data)
        return Response(
            transaction_serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

    def _create_balance(self, request: Request, target: Target):
        user_balance = Transaction.objects.get_queryset().aggregate_balance()['balance']
        if Decimal(request.data['amount']) > user_balance:
            raise TargetBalanceTotalException
        else:
            balance_serializer = TargetBalanceSerializer(
                context={
                    'request': request,
                },
                data={'data': request.data,
                      'transactions': {
                          'category': request.data['category'],
                          'amount': request.data['amount'],
                          'transaction_type': TransactionTypes.EXPENSE,
                      },
                      },
            )
            balance_serializer.is_valid(raise_exception=True)
            balance = balance_serializer.save()
            target.balance = balance
            target.save()
