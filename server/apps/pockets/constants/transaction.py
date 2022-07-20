from typing import Final


class TransactionTypes:
    INCOME: Final[str] = 'income'
    EXPENSE: Final[str] = 'expense'

    CHOICES: Final[tuple[tuple[str, str], ...]] = (
        (INCOME, 'Доход'),
        (EXPENSE, 'Расход'),
    )

    CHOICES_DICT: Final[dict[str, str]] = dict(CHOICES)
