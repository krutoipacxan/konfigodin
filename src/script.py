"""Выполнение стартового скрипта с имитацией диалога."""

from src.errors import ScriptError


def read_script(path):
    """Прочитать строки скрипта; при неудаче бросить ScriptError."""
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return handle.read().splitlines()
    except FileNotFoundError:
        raise ScriptError(f"script not found: {path}") from None
    except OSError as error:
        raise ScriptError(f"cannot read {path}: {error.strerror}") from None
    except UnicodeDecodeError:
        raise ScriptError(f"script is not a UTF-8 text: {path}") from None


def run_script(shell, path):
    """Выполнить скрипт: показать ввод и вывод, пропуская ошибки.

    Пустые строки пропускаются. Возвращает число ошибочных строк.
    """
    failed = 0
    for number, line in enumerate(read_script(path), start=1):
        if not line.strip():
            continue
        shell.say(shell.prompt() + line)
        if not shell.run_line(line):
            failed += 1
            shell.complain(f"script: {path}: line {number}: skipped (error)")
    return failed
