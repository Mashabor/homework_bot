"""Мои исключения."""


class MessageError(Exception):
    """Ошибка при отправке сообщения."""

    pass


class VariablesError(Exception):
    """Ошибка переменных окружения."""

    pass
