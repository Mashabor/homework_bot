"""Мои исключения."""


class MessageError(Exception):
    """Ошибка при отправке сообщения."""

    pass


class StatusCodeError(Exception):
    """Ошибка доступности ресурса."""

    pass
