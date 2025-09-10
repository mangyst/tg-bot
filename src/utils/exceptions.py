# Кастомные исключения

class UserCreateError(Exception):
    """Ошибка создания пользователя."""

    def __str__(self):
        return "Бот не может в данный момент создать пользователя"


class UserReadError(Exception):
    """Ошибка получения пользователя."""

    def __str__(self):
        return "Бот не может в данный момент найти пользователя"


class UserOperationError(Exception):
    """Ошибка выполнения операции с характеристиками."""

    def __str__(self):
        return "Бот не может в данный момент выполнить операцию."


class DeficitStatsError(Exception):
    """Ошибка при попытке установить статов больше допустимого."""

    def __str__(self):
        return "Недостаточно свободных очков для установки характеристик."
