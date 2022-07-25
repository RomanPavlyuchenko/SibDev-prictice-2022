from django.db.models import Manager

from ..querysets import TargetQuerySet


class TargetManager(Manager):
    def get_queryset(self, **kwargs) -> TargetQuerySet:
        return TargetQuerySet(
            self.model,
            using=self._db,
        )

    def aggregate_total(self):
        return self.get_queryset().aggregate_total()
