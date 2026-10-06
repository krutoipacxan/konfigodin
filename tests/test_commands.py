"""Тесты команд ls, cd, rev, echo на VFS tests/vfs/deep.json."""

import io
import os
import unittest

from src.shell import Shell
from src.vfs import load_vfs

DEEP = os.path.join(os.path.dirname(__file__), "vfs", "deep.json")


class CommandTestCase(unittest.TestCase):
    """Общая подготовка: оболочка с перехватом вывода."""

    def setUp(self):
        self.out, self.err = io.StringIO(), io.StringIO()
        self.shell = Shell("bob", "box", self.out, self.err, load_vfs(DEEP))

    def run_ok(self, line):
        """Выполнить команду, ожидая успех; вернуть вывод."""
        self.out.truncate(0)
        self.out.seek(0)
        self.assertTrue(self.shell.run_line(line), self.err.getvalue())
        return self.out.getvalue()

    def run_fail(self, line):
        """Выполнить команду, ожидая ошибку; вернуть текст ошибки."""
        self.err.truncate(0)
        self.err.seek(0)
        self.assertFalse(self.shell.run_line(line))
        return self.err.getvalue()


class LsTest(CommandTestCase):
    """Режимы команды ls."""

    def test_plain_hides_dotfiles(self):
        self.assertEqual(self.run_ok("ls"), "bin  docs  readme.txt\n")

    def test_all_shows_dotfiles(self):
        self.assertIn(".hidden", self.run_ok("ls -a"))

    def test_path_argument(self):
        self.assertEqual(self.run_ok("ls docs"), "notes.txt  projects\n")

    def test_long_format(self):
        out = self.run_ok("ls -l docs/notes.txt")
        self.assertEqual(
            out, "- alice    staff        23 docs/notes.txt\n"
        )

    def test_several_paths_have_titles(self):
        out = self.run_ok("ls bin docs/projects")
        self.assertIn("bin:\ntool", out)
        self.assertIn("docs/projects:\nalpha  beta.txt", out)

    def test_errors(self):
        self.assertIn("No such file", self.run_fail("ls /nope"))
        self.assertIn("invalid option", self.run_fail("ls -z"))


class CdTest(CommandTestCase):
    """Режимы команды cd."""

    def test_relative_and_back(self):
        self.run_ok("cd docs/projects")
        self.assertEqual(self.shell.cwd, ["docs", "projects"])
        self.run_ok("cd ../..")
        self.assertEqual(self.shell.cwd, [])

    def test_without_args_goes_to_root(self):
        self.run_ok("cd docs")
        self.run_ok("cd")
        self.assertEqual(self.shell.cwd, [])

    def test_absolute_and_tilde(self):
        self.run_ok("cd /docs")
        self.run_ok("cd ~/bin")
        self.assertEqual(self.shell.cwd, ["bin"])

    def test_errors(self):
        self.assertIn("No such file", self.run_fail("cd nope"))
        self.assertIn("Not a directory", self.run_fail("cd readme.txt"))
        self.assertIn("too many", self.run_fail("cd a b"))

    def test_ls_is_relative_to_cwd(self):
        self.run_ok("cd docs")
        self.assertEqual(self.run_ok("ls"), "notes.txt  projects\n")


class RevEchoTest(CommandTestCase):
    """Команды rev и echo."""

    def test_rev_file(self):
        self.assertEqual(
            self.run_ok("rev docs/notes.txt"), "enil tsrif\nenil dnoces\n"
        )

    def test_rev_several_files(self):
        out = self.run_ok("rev readme.txt docs/projects/beta.txt")
        self.assertEqual(out, "!SFV ,olleH\nateb\n")

    def test_rev_errors(self):
        self.assertIn("missing operand", self.run_fail("rev"))
        self.assertIn("Is a directory", self.run_fail("rev docs"))
        self.assertIn("No such file", self.run_fail("rev nope.txt"))

    def test_echo(self):
        self.assertEqual(self.run_ok("echo a   b  c"), "a b c\n")

    def test_echo_without_args_prints_nothing(self):
        self.assertEqual(self.run_ok("echo"), "")


class ChownTest(CommandTestCase):
    """Режимы команды chown."""

    def owner_of(self, path):
        """Вернуть пару (владелец, группа) узла."""
        _, node = self.shell.vfs.resolve(path, [])
        return node.owner, node.group

    def test_owner_only(self):
        self.run_ok("chown bob readme.txt")
        self.assertEqual(self.owner_of("readme.txt"), ("bob", "root"))

    def test_owner_and_group(self):
        self.run_ok("chown bob:users readme.txt")
        self.assertEqual(self.owner_of("readme.txt"), ("bob", "users"))

    def test_group_only(self):
        self.run_ok("chown :users readme.txt")
        self.assertEqual(self.owner_of("readme.txt"), ("root", "users"))

    def test_several_paths(self):
        self.run_ok("chown bob readme.txt bin")
        self.assertEqual(self.owner_of("bin")[0], "bob")

    def test_directory_without_recursion(self):
        self.run_ok("chown bob docs")
        self.assertEqual(self.owner_of("docs")[0], "bob")
        self.assertEqual(self.owner_of("docs/notes.txt")[0], "alice")

    def test_recursive(self):
        self.run_ok("chown -R bob:dev docs")
        for path in ("docs", "docs/projects/alpha/todo.txt"):
            self.assertEqual(self.owner_of(path), ("bob", "dev"))

    def test_visible_in_ls(self):
        self.run_ok("chown bob readme.txt")
        self.assertIn("- bob ", self.run_ok("ls -l"))

    def test_relative_to_cwd(self):
        self.run_ok("cd docs")
        self.run_ok("chown bob notes.txt")
        self.assertEqual(self.owner_of("docs/notes.txt")[0], "bob")

    def test_errors(self):
        self.assertIn("missing operand", self.run_fail("chown"))
        self.assertIn("missing operand", self.run_fail("chown bob"))
        self.assertIn("No such file", self.run_fail("chown bob nope"))
        self.assertIn("invalid user", self.run_fail("chown 1x readme.txt"))
        self.assertIn("invalid user", self.run_fail("chown : readme.txt"))
        self.assertIn("invalid option", self.run_fail("chown -x a b"))
