from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from .managers import TargetBalanceManager
from ..models import Target


def create_daily_percent():
    targets = Target.objects.get_queryset().annotate_daily_percent()
    targets_percent = [
        TargetBalance(
            amount=target.daily_percent,
            target=target,
            is_percent=True,
        ) for target in targets
    ]
    TargetBalance.objects.bulk_create(targets_percent)
    return len(targets_percent)


class TargetBalance(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма операции',
        validators=(MinValueValidator(Decimal('0.01')),),
    )
    transaction_date = models.DateField(
        verbose_name='Дата операции',
        default=date.today
    )
    target = models.ForeignKey(
        to='targets.Target',
        on_delete=models.CASCADE,
        related_name='balances',
        verbose_name='Цель',
    )
    is_percent = models.BooleanField(
        verbose_name='Способ пополнения',
        default=False,
    )

    objects = TargetBalanceManager()

    class Meta:
        verbose_name = 'Баланс'
