"""Точка входа: сборка оболочки и запуск диалога."""

import sys

from src.config import format_debug, parse_args
from src.errors import ScriptError, ShellExit
from src.script import run_script
from src.shell import Shell, enable_line_editing

EXIT_OK = 0
EXIT_FAILURE = 1


def run_shell(shell, config):
    """Выполнить стартовый скрипт (если задан), затем запустить REPL."""
    if config.script:
        run_script(shell, config.script)
    shell.repl()


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения процесса."""
    config = parse_args(argv)
    for line in format_debug(config):
        print(line)
    enable_line_editing()
    try:
        run_shell(Shell(), config)
    except ScriptError as error:
        print(f"emulator: {error}", file=sys.stderr)
        return EXIT_FAILURE
    except ShellExit as stop:
        return stop.code
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
