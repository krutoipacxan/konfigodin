"""Тесты параметров командной строки."""

import unittest

from src.config import Config, format_debug, parse_args


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров и отладочного вывода."""

    def test_defaults(self):
        self.assertEqual(parse_args([]), Config())

    def test_both_params(self):
        config = parse_args(["--vfs", "a.json", "--script", "b.esh"])
        self.assertEqual(config, Config(vfs="a.json", script="b.esh"))

    def test_unknown_param_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])

    def test_debug_lists_all_params(self):
        lines = format_debug(Config(vfs="a.json"))
        text = "\n".join(lines)
        self.assertIn("--vfs    = a.json", text)
        self.assertIn("--script = (not set)", text)
