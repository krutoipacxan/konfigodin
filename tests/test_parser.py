"""Тесты разбора строки на команду и аргументы."""

import unittest

from src.parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки функции parse_line."""

    def test_command_and_args(self):
        self.assertEqual(parse_line("ls -l /tmp"), ("ls", ["-l", "/tmp"]))

    def test_extra_spaces(self):
        self.assertEqual(parse_line("  cd   a  "), ("cd", ["a"]))

    def test_empty_line(self):
        self.assertEqual(parse_line("   "), (None, []))
