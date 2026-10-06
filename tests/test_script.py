"""Тесты выполнения стартового скрипта и запуска приложения."""

import contextlib
import io
import os
import tempfile
import unittest

from src.app import main
from src.errors import ScriptError
from src.script import read_script, run_script
from src.shell import Shell


def write_temp(text):
    """Записать текст во временный файл и вернуть его путь."""
    handle, path = tempfile.mkstemp(suffix=".esh")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(text)
    return path


class ScriptTest(unittest.TestCase):
    """Проверки run_script и read_script."""

    def setUp(self):
        self.out, self.err = io.StringIO(), io.StringIO()
        self.shell = Shell("bob", "box", self.out, self.err)

    def test_shows_input_and_output(self):
        path = write_temp("ls a\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(run_script(self.shell, path), 0)
        self.assertEqual(
            self.out.getvalue(),
            "bob@box:~$ ls a\nls: args=['a']\n",
        )

    def test_skips_bad_lines_and_reports(self):
        path = write_temp("foo\n\nls\ncd a b\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(run_script(self.shell, path), 2)
        self.assertIn("line 1: skipped", self.err.getvalue())
        self.assertIn("line 4: skipped", self.err.getvalue())
        self.assertIn("ls: args=[]", self.out.getvalue())

    def test_missing_script(self):
        with self.assertRaises(ScriptError):
            read_script("/no/such/script.esh")


class AppTest(unittest.TestCase):
    """Проверки кодов возврата main."""

    def run_main(self, argv):
        """Запустить main, скрыв вывод, и вернуть код возврата."""
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            with contextlib.redirect_stderr(sink):
                return main(argv)

    def test_exit_code_from_script(self):
        path = write_temp("exit 7\n")
        self.addCleanup(os.remove, path)
        self.assertEqual(self.run_main(["--script", path]), 7)

    def test_missing_script_fails(self):
        self.assertEqual(self.run_main(["--script", "/no/such"]), 1)
