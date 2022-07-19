from typing import Type

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filterset import TransactionCategoryFilter
from ..models import TransactionCategory
from ..models.querysets import TransactionCategoryQuerySet
from ..serializers import (
    TransactionCategorySerializer,
    TransactionCategoryTransactionSumSerializer,
    TransactionCategoryTransactionsSerializer,
)


class TransactionCategoryViewSet(viewsets.mixins.ListModelMixin,
                                 viewsets.mixins.CreateModelMixin,
                                 viewsets.GenericViewSet):

    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionCategoryFilter

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        if self.action == 'transactions_by_categories':
            serializer_class = TransactionCategoryTransactionSumSerializer
        elif self.action == 'top_categories':
            serializer_class = TransactionCategoryTransactionsSerializer
        else:
            serializer_class = TransactionCategorySerializer

        return serializer_class

    def get_queryset(self) -> TransactionCategoryQuerySet:
        queryset = TransactionCategory.objects.filter(
            user=self.request.user,
        ).order_by('-id')

        if self.action in ('transactions_by_categories', 'list', 'top_categories',):
            queryset = queryset.annotate_with_transaction_sums()

        return queryset

    @action(methods=('GET',), detail=False, url_path='transactions-by-categories')
    def transactions_by_categories(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    @action(methods=('GET',), detail=False, url_path='top-categories-by-transactions')
    def top_categories(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset()).get_list_top_categories()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
