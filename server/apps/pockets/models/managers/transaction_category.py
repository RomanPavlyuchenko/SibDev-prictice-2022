from django.db.models import Manager
from typing import List
from decimal import Decimal

from ..querysets import TransactionCategoryQuerySet


class TransactionCategoryManager(Manager):
    def get_queryset(self, **kwargs) -> TransactionCategoryQuerySet:
        return TransactionCategoryQuerySet(self.model, using=self._db)

    def annotate_with_transaction_sums(self) -> 'TransactionCategoryQuerySet':
        return self.get_queryset().annotate_with_transaction_sums()

    def get_list_top_categories(self) -> List[dict[str, Decimal]]:
        return self.get_queryset().get_list_top_categories()
