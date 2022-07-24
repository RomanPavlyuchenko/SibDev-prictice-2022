from typing import Final
from rest_framework.exceptions import ValidationError


class TargetErrors:
    ALREADY_EXISTS: Final[str] = 'У пользоваетля уже существует цель с таким названием'
    NOT_USERS_CATEGORY: Final[str] = 'У пользователя нет такой категории'
    TARGET_AMOUNT_TOO_LOW: Final[str] = 'Желаемая сумма не может быть меньше текущей'
    BALANCE_TOO_LOW: Final[str] = 'Недостаточно средств на счете'
    FIELD_NOT_EDITABLE: Final[str] = 'Изменение поля запрещено'
