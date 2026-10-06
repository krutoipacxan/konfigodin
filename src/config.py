"""Параметры командной строки и их отладочный вывод."""

import argparse
from dataclasses import dataclass

NOT_SET = "(not set)"


@dataclass
class Config:
    """Параметры запуска эмулятора."""

    vfs: str = None
    script: str = None


def build_parser():
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор языка оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="путь к стартовому скрипту",
    )
    return parser


def parse_args(argv=None):
    """Разобрать параметры и вернуть объект Config."""
    namespace = build_parser().parse_args(argv)
    return Config(vfs=namespace.vfs, script=namespace.script)


def format_debug(config):
    """Вернуть строки отладочного вывода всех заданных параметров."""
    return [
        "[debug] emulator parameters:",
        f"[debug]   --vfs    = {config.vfs or NOT_SET}",
        f"[debug]   --script = {config.script or NOT_SET}",
    ]
