from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .managers import TargetBalanceManager


class TargetBalance(models.Model):
    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Планируемая сумма',
        validators=(
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('100.00')),
        ),
        default=Decimal('0.00'),
    )

    objects = TargetBalanceManager()

    class Meta:
        verbose_name = 'Баланс'
