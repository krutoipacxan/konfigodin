"""Тесты оболочки: приглашение, заглушки, ошибки и REPL."""

import io
import unittest

from src.errors import ShellExit
from src.shell import Shell


def make_shell():
    """Создать оболочку с перехватом вывода."""
    out, err = io.StringIO(), io.StringIO()
    return Shell(user="bob", host="box", out=out, err=err), out, err


class ShellTest(unittest.TestCase):
    """Проверки класса Shell."""

    def test_prompt(self):
        shell, _, _ = make_shell()
        self.assertEqual(shell.prompt(), "bob@box:~$ ")

    def test_prompt_follows_cwd(self):
        shell, _, _ = make_shell()
        shell.run_line("cd docs")
        self.assertEqual(shell.prompt(), "bob@box:~/docs$ ")

    def test_unknown_command(self):
        shell, _, err = make_shell()
        self.assertFalse(shell.run_line("foo"))
        self.assertEqual(err.getvalue(), "foo: command not found\n")

    def test_bad_arguments(self):
        shell, _, err = make_shell()
        self.assertFalse(shell.run_line("cd a b"))
        self.assertIn("too many arguments", err.getvalue())

    def test_exit_code(self):
        shell, _, _ = make_shell()
        with self.assertRaises(ShellExit) as caught:
            shell.run_line("exit 3")
        self.assertEqual(caught.exception.code, 3)

    def test_exit_bad_code(self):
        shell, _, err = make_shell()
        self.assertFalse(shell.run_line("exit abc"))
        self.assertIn("numeric argument required", err.getvalue())

    def test_repl_stops_on_eof(self):
        shell, out, _ = make_shell()
        shell.reader = lambda prompt: (_ for _ in ()).throw(EOFError())
        shell.repl()
        self.assertEqual(out.getvalue(), "exit\n")


class VfsInfoTest(unittest.TestCase):
    """Служебная команда vfs-info."""

    def test_default_vfs_stats(self):
        shell, out, _ = make_shell()
        shell.run_line("vfs-info")
        self.assertEqual(
            out.getvalue(), "directories: 2\nfiles: 2\nmax depth: 2\n"
        )
