from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, pagination, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filtersets import TargetFilter
from ..models import Target, TargetBalance
from ..models.querysets import TargetQuerySet
from ..serializers import TargetCreateSerializer, TargetRetrieveSerializer, TargetBalanceSerializer
from ..serializers.target import TargetListSerializer
from ...pockets.constants import TransactionTypes
from ...pockets.serializers import TransactionCreateSerializer


class TargetViewSet(viewsets.ModelViewSet):
    pagination_class = pagination.LimitOffsetPagination
    pagination_class.default_limit = 20
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TargetFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update',):
            serializer_class = TargetCreateSerializer
        elif self.action in ('retrieve',):
            serializer_class = TargetRetrieveSerializer
        else:
            serializer_class = TargetListSerializer
        return serializer_class

    def get_queryset(self) -> TargetQuerySet:
        queryset = Target.objects.filter(
            user=self.request.user,
        ).prefetch_related('balances').order_by(
            '-create_date',
        )
        if self.action == 'list':
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

        if 'initial_amount' in request.data:
            target.balances.add(self._create_balance(request, *args, **kwargs))
            target.save()

        headers = self.get_success_headers(target_serializer.data)
        return Response(
            target_serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.initial_payment and 'initial_payment' in request.data:
            instance.balances.add(self._create_balance(request, *args, **kwargs))
            instance.save()

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if timezone.now().date() < self.get_queryset().filter(pk=kwargs['pk']).first().deadline:
            total = self.get_queryset().filter(
                pk=kwargs['pk']
            ).aggregate_total()['total']

            transaction_serializer = TransactionCreateSerializer(
                context={'request': request},
                data={
                    'transaction_type': TransactionTypes.INCOME,
                    'amount': total,
                },
            )
            transaction_serializer.is_valid(raise_exception=True)
            transaction_serializer.save()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def _create_balance(self, request: Request, *args, **kwargs) -> TargetBalance:
        instance = self.get_object()
        if 'initial_payment' in request.data:
            amount = request.data['initial_payment']
        else:
            amount = request.data.get('amount', None)
        data = {
            'category': instance.category.id,
            'transaction_type': TransactionTypes.EXPENSE,
            'amount': amount,
            'target': instance.id,
        }

        transaction_serializer = TransactionCreateSerializer(
            context={'request': request},
            data=data,
        )
        transaction_serializer.is_valid(raise_exception=True)
        transaction_serializer.save()

        balance_serializer = TargetBalanceSerializer(
            context={'request': request},
            data=data,
        )
        balance_serializer.is_valid(raise_exception=True)

        return balance_serializer.save()
