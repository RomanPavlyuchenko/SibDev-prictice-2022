from typing import Final


class TargetErrors:
    ALREADY_EXISTS: Final[str] = 'У пользоваетля уже существует цель с таким названием'
    NOT_USERS_CATEGORY: Final[str] = 'У пользователя нет такой категории'
    TARGET_AMOUNT_TOO_LOW: Final[str] = 'Желаемая сумма не может быть меньше текущей'
    BALANCE_TOO_LOW: Final[str] = 'Недостаточно средств на счете'
    TARGET_TERM_TOO_LOW: Final[str] = 'Нельзя изменить дату завершения цели в меньшую сторону'
    FIELD_NOT_EDITABLE: Final[str] = 'Нельзя повторно менять первоначальный взнос'


class TargetBalanceErrors:
    BALANCE_TOO_LOW: Final[str] = 'Недостаточно средств на счете'
