"""Точка входа: сборка оболочки и запуск диалога."""

import sys

from src.errors import ShellExit
from src.shell import Shell, enable_line_editing

EXIT_OK = 0


def main():
    """Запустить эмулятор и вернуть код завершения процесса."""
    enable_line_editing()
    shell = Shell()
    try:
        shell.repl()
    except ShellExit as stop:
        return stop.code
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
