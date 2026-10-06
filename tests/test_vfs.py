"""Тесты виртуальной файловой системы."""

import os
import unittest

from src.vfs import (
    VfsError, VfsLoadError, build_vfs, collect_stats, default_vfs,
    load_vfs,
)

VFS_DIR = os.path.join(os.path.dirname(__file__), "vfs")


def sample(name):
    """Вернуть путь к образцу VFS из tests/vfs."""
    return os.path.join(VFS_DIR, name)


class LoadTest(unittest.TestCase):
    """Загрузка VFS из JSON."""

    def test_minimal(self):
        vfs = load_vfs(sample("minimal.json"))
        self.assertEqual(collect_stats(vfs.root), (1, 0, 0))

    def test_files(self):
        vfs = load_vfs(sample("files.json"))
        self.assertEqual(collect_stats(vfs.root), (1, 3, 1))

    def test_deep_has_three_levels(self):
        vfs = load_vfs(sample("deep.json"))
        _, _, depth = collect_stats(vfs.root)
        self.assertGreaterEqual(depth, 3)

    def test_base64_content(self):
        vfs = load_vfs(sample("binary.json"))
        _, node = vfs.resolve("data.bin", [])
        self.assertEqual(node.data, b"\x89PNG\r\n\x1a\n")

    def test_default_vfs(self):
        self.assertTrue(default_vfs().root.is_dir)

    def test_missing_file(self):
        with self.assertRaisesRegex(VfsLoadError, "not found"):
            load_vfs(sample("missing.json"))

    def test_invalid_files(self):
        for name in ("invalid_json", "invalid_node", "invalid_base64"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(VfsLoadError, "invalid VFS"):
                    load_vfs(sample(name + ".json"))

    def test_root_must_be_dir(self):
        with self.assertRaises(VfsLoadError):
            build_vfs({"type": "file"})

    def test_bad_entry_name(self):
        raw = {"type": "dir", "children": {"a/b": {"type": "dir"}}}
        with self.assertRaises(VfsLoadError):
            build_vfs(raw)


class ResolveTest(unittest.TestCase):
    """Поиск узлов по пути."""

    def setUp(self):
        self.vfs = load_vfs(sample("deep.json"))

    def test_absolute_and_relative(self):
        parts, _ = self.vfs.resolve("/docs/projects", [])
        self.assertEqual(parts, ["docs", "projects"])
        parts, _ = self.vfs.resolve("alpha/..", parts)
        self.assertEqual(parts, ["docs", "projects"])

    def test_dotdot_stops_at_root(self):
        parts, _ = self.vfs.resolve("../../..", ["docs"])
        self.assertEqual(parts, [])

    def test_missing_path(self):
        with self.assertRaises(VfsError):
            self.vfs.resolve("/nope", [])

    def test_file_is_not_a_directory(self):
        with self.assertRaises(VfsError):
            self.vfs.resolve("/readme.txt/x", [])
