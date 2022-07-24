from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from .managers import TargetBalanceManager


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

    objects = TargetBalanceManager()

    class Meta:
        verbose_name = 'Баланс'
