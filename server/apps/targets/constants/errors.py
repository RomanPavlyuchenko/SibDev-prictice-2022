from typing import Final
from rest_framework.exceptions import ValidationError


class TargetErrors:
    ALREADY_EXISTS: Final[str] = 'У пользоваетля уже существует цель с таким названием'
    NOT_USERS_CATEGORY: Final[str] = 'У пользователя нет такой категории'
    EXPECTED_AMOUNT_TOO_LOW: Final[str] = 'Желаемая сумма не может быть меньше текущей'


class TargetBalanceTotalException(ValidationError):
    default_code = 'Недостаточно средств'
    default_detail = 'Недостаточно средств.'
