from datetime import date
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator

from .managers import TargetManager


class Target(models.Model):
    user = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='targets',
        verbose_name='Пользователь',
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
    )
    create_date = models.DateField(
        default=date.today,
        verbose_name='Дата создания'
    )
    target_deadline = models.DateField(
        verbose_name='Срок цели'
    )
    balance = models.OneToOneField(
        to='targets.TargetBalance',
        on_delete=models.CASCADE,
        related_name='target',
        verbose_name='Баланс',
        null=True,
        blank=True,
    )
    expected_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма операции',
        validators=(MinValueValidator(Decimal('0.01')),),
    )
    category = models.ForeignKey(
        to='pockets.TransactionCategory',
        on_delete=models.CASCADE,
        related_name='targets',
        verbose_name='Категория',
    )

    objects = TargetManager()

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self) -> str:
        return f'{self.name}'
