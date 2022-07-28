from typing import Final


class TargetBalanceTypes:
    USER: Final[str] = 'user'
    PERCENT: Final[str] = 'percent'

    CHOICES: Final[tuple[tuple[str, str], ...]] = (
        (USER, 'Пользователь'),
        (PERCENT, 'Начисление процентов'),
    )

    CHOICES_DICT: Final[dict[str, str]] = dict(CHOICES)
