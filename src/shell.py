"""Оболочка: приглашение, выполнение строк и цикл REPL."""

import importlib
import sys

from src.commands import COMMANDS
from src.errors import ShellError
from src.parser import parse_line
from src.system import get_hostname, get_username


def enable_line_editing():
    """Подключить readline (история и правка строки), если он есть."""
    try:
        importlib.import_module("readline")
    except ImportError:
        return False
    return True


class Shell:
    """Состояние эмулятора и логика диалога с пользователем."""

    def __init__(self, user=None, host=None, out=None, err=None):
        """Создать оболочку; имя и хост по умолчанию берутся из ОС."""
        self.user = user or get_username()
        self.host = host or get_hostname()
        self.out = out
        self.err = err
        self.reader = input

    def say(self, text):
        """Вывести текст в стандартный поток вывода."""
        print(text, file=self.out or sys.stdout)

    def complain(self, text):
        """Вывести текст в поток ошибок."""
        print(text, file=self.err or sys.stderr)

    def prompt(self):
        """Сформировать приглашение вида username@hostname:~$ ."""
        return f"{self.user}@{self.host}:~$ "

    def execute(self, line):
        """Выполнить строку и вернуть вывод команды (или None)."""
        name, args = parse_line(line)
        if name is None:
            return None
        handler = COMMANDS.get(name)
        if handler is None:
            raise ShellError(f"{name}: command not found")
        return handler(self, args)

    def run_line(self, line):
        """Выполнить строку, показав вывод или ошибку.

        Возвращает True при успехе и False при ошибке команды.
        Исключение ShellExit пробрасывается наружу.
        """
        try:
            output = self.execute(line)
        except ShellError as error:
            self.complain(str(error))
            return False
        if output:
            self.say(output)
        return True

    def repl(self):
        """Читать и выполнять команды, пока не придёт exit или EOF."""
        while True:
            try:
                line = self.reader(self.prompt())
            except EOFError:
                self.say("exit")
                return
            except KeyboardInterrupt:
                self.say("")
                continue
            self.run_line(line)
