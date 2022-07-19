from typing import Final


class TransactionErrors:
    NOT_USERS_CATEGORY: Final[str] = 'У пользователя нет такой категории'
    FIELD_IS_REQUIRED: Final[str] = 'Поле категория обязательно для транзакции типа расход'
    INCOME_TRANSACTION_TYPE: Final[str] = 'У транзакций типа доход не может быть категории'


class TransactionCategoryErrors:
    ALREADY_EXISTS: Final[str] = 'У пользоваетля уже существует категория с таким названием и типом'
