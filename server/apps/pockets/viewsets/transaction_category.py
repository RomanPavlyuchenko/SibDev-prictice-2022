from typing import Type

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filterset import TransactionCategoryFilter
from ..models import TransactionCategory
from ..serializers import (
    TransactionCategorySerializer,
    TransactionCategoryTransactionSumSerializer,
)


class TransactionCategoryViewSet(viewsets.ReadOnlyModelViewSet,
                                 viewsets.mixins.CreateModelMixin):

    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TransactionCategoryFilter

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        if self.action == 'transactions_by_categories':
            serializer_class = TransactionCategoryTransactionSumSerializer
        else:
            serializer_class = TransactionCategorySerializer

        return serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = TransactionCategory.objects.filter(
            user=self.request.user,
        ).order_by('-id')

        if self.action == 'transactions_by_categories' or self.action == 'list':
            queryset = queryset.annotate_with_transaction_sums()

        return queryset

    @action(methods=('GET',), detail=False, url_path='transactions-by-categories')
    def transactions_by_categories(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)
