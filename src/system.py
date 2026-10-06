"""Данные реальной ОС для формирования приглашения к вводу."""

import getpass
import socket

FALLBACK_USER = "user"


def get_username():
    """Вернуть имя пользователя ОС, запустившего эмулятор."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return FALLBACK_USER


def get_hostname():
    """Вернуть короткое сетевое имя компьютера."""
    return socket.gethostname().split(".")[0]
