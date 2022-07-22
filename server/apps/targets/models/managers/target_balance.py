from django.db.models import Manager

from ..querysets import TargetBalanceQuerySet


class TargetBalanceManager(Manager):
    def get_queryset(self, **kwargs) -> TargetBalanceQuerySet:
        return TargetBalanceQuerySet(
            self.model,
            using=self._db,
        )

    def annotate_with_transaction_sums(self) -> TargetBalanceQuerySet:
        return self.get_queryset().annotate_with_transaction_sums()
