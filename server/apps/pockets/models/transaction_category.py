from django.db import models

from .managers import TransactionCategoryManager
# from ..constants import CategoryTypes


class TransactionCategory(models.Model):
    user = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Пользователь',
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название',
    )
    # category_type = models.CharField(
    #     max_length=7,
    #     choices=CategoryTypes.CHOICES,
    #     verbose_name='Тип категории',
    # )

    objects = TransactionCategoryManager()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    # def __str__(self) -> str:
    #     return f'{self.name} ({CategoryTypes.CHOICES_DICT[self.category_type]})'
