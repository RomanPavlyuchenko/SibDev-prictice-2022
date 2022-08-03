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

    def get_daily_percent(self):
        return self.get_queryset().filter(
            is_closed=False
        ).prefetch_related(
            'balances'
        ).annotate_daily_percent()
