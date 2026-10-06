"""Исключения эмулятора."""


class ShellError(Exception):
    """Ошибка выполнения команды; текст показывается пользователю."""


class ShellExit(Exception):
    """Запрос на завершение работы эмулятора."""

    def __init__(self, code=0):
        """Запомнить код возврата процесса."""
        super().__init__(code)
        self.code = code


class ScriptError(Exception):
    """Стартовый скрипт невозможно прочитать или выполнить."""
