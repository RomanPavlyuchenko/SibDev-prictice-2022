from datetime import date
from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

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
    target_term = models.PositiveSmallIntegerField(
        verbose_name='Срок цели в месяцах',
        validators=(MinValueValidator(1),),
    )
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Целевая сумма',
        validators=(MinValueValidator(Decimal('0.01')),),
    )
    category = models.ForeignKey(
        to='pockets.TransactionCategory',
        on_delete=models.CASCADE,
        related_name='targets',
        verbose_name='Категория',
    )
    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Процент',
        validators=(
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('100.00')),
        ),
        default=Decimal('0.00'),
    )
    initial_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Первоначальный взнос',
        validators=(MinValueValidator(Decimal('0.01')),),
        default=Decimal(0)
    )
    is_closed = models.BooleanField(
        verbose_name='Цель открыта',
        default=False,
    )
    closing_date = models.DateField(
        default=None,
        null=True,
    )

    objects = TargetManager()

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self) -> str:
        return f'{self.name}'
