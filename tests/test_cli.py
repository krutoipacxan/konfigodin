"""Сквозные тесты: запуск эмулятора как процесса."""

import glob
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEEP = os.path.join(ROOT, "tests", "vfs", "deep.json")


def run_emulator(*args):
    """Запустить python3 -m src с пустым stdin и вернуть результат."""
    return subprocess.run(
        [sys.executable, "-m", "src", *args],
        cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True,
        text=True, check=False,
    )


class CliTest(unittest.TestCase):
    """Проверки процесса эмулятора."""

    def test_all_emulator_scripts_run_without_crash(self):
        pattern = os.path.join(ROOT, "tests", "emu", "*.esh")
        for script in sorted(glob.glob(pattern)):
            with self.subTest(script=os.path.basename(script)):
                result = run_emulator("--vfs", DEEP, "--script", script)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(result.returncode, 0)

    def test_chown_does_not_modify_vfs_file(self):
        with open(DEEP, "rb") as handle:
            before = handle.read()
        script = os.path.join(ROOT, "tests", "emu", "stage5_chown.esh")
        run_emulator("--vfs", DEEP, "--script", script)
        with open(DEEP, "rb") as handle:
            self.assertEqual(handle.read(), before)

    def test_bad_vfs_exit_code(self):
        result = run_emulator("--vfs", "no_such_file.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("VFS file not found", result.stderr)
