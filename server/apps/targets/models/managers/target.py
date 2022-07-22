from django.db.models import Manager

from ..querysets import TargetQuerySet


class TargetManager(Manager):
    def get_queryset(self, **kwargs) -> TargetQuerySet:
        return TargetQuerySet(
            self.model,
            using=self._db,
        )
