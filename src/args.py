"""Вспомогательные функции проверки аргументов команд."""

from src.errors import ShellError


def check_arg_count(name, args, minimum, maximum):
    """Проверить число аргументов команды.

    Параметр maximum может быть None, если верхней границы нет.
    """
    if len(args) < minimum:
        raise ShellError(f"{name}: missing operand")
    if maximum is not None and len(args) > maximum:
        raise ShellError(f"{name}: too many arguments")


def validate_flags(name, arg, allowed):
    """Проверить набор флагов вида -abc и вернуть их множеством."""
    for letter in arg[1:]:
        if letter not in allowed:
            raise ShellError(f"{name}: invalid option -- '{letter}'")
    return set(arg[1:])


def split_flags(name, args, allowed):
    """Отделить флаги от операндов.

    Возвращает кортеж (множество флагов, список операндов). Одиночный
    дефис считается операндом.
    """
    flags = set()
    operands = []
    for arg in args:
        if arg.startswith("-") and len(arg) > 1:
            flags.update(validate_flags(name, arg, allowed))
        else:
            operands.append(arg)
    return flags, operands
