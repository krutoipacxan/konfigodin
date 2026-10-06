"""Виртуальная файловая система, целиком хранящаяся в памяти."""

import base64
import binascii
import json
import re
from dataclasses import dataclass, field

TYPE_DIR = "dir"
TYPE_FILE = "file"
ENCODING_TEXT = "utf-8"
ENCODING_BASE64 = "base64"
DEFAULT_OWNER = "root"
DEFAULT_GROUP = "root"
DIR_SIZE = 4096
NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
RESERVED_NAMES = ("", ".", "..")

DEFAULT_TREE = {
    "type": TYPE_DIR,
    "children": {
        "readme.txt": {
            "type": TYPE_FILE,
            "content": "Welcome to the shell emulator!\n",
        },
        "docs": {
            "type": TYPE_DIR,
            "children": {
                "notes.txt": {"type": TYPE_FILE, "content": "first note\n"},
            },
        },
    },
}


class VfsError(Exception):
    """Ошибка обращения к узлу VFS (нет пути, не каталог и т. п.)."""


class VfsLoadError(Exception):
    """Ошибка загрузки VFS: файл не найден или неверный формат."""


@dataclass
class Node:
    """Узел дерева VFS: файл или каталог."""

    is_dir: bool
    owner: str = DEFAULT_OWNER
    group: str = DEFAULT_GROUP
    data: bytes = b""
    children: dict = field(default_factory=dict)

    @property
    def size(self):
        """Размер узла в байтах (для каталога — условный)."""
        return DIR_SIZE if self.is_dir else len(self.data)


def is_valid_name(value):
    """Проверить имя пользователя или группы."""
    return bool(NAME_PATTERN.fullmatch(value))


def path_segments(path, cwd):
    """Разбить путь на сегменты, учитывая текущий каталог cwd."""
    if path.startswith("/"):
        return path.split("/")
    if path == "~" or path.startswith("~/"):
        return path[1:].split("/")
    return list(cwd) + path.split("/")


class Vfs:
    """Дерево узлов и поиск по пути."""

    def __init__(self, root):
        """Создать VFS с корневым каталогом root."""
        self.root = root

    def resolve(self, path, cwd):
        """Найти узел по пути.

        Возвращает кортеж (список компонентов от корня, узел).
        При неудаче бросает VfsError.
        """
        parts, nodes = [], [self.root]
        for segment in path_segments(path, cwd):
            self.advance(parts, nodes, segment)
        return parts, nodes[-1]

    @staticmethod
    def advance(parts, nodes, segment):
        """Сделать один шаг по пути, изменяя parts и nodes."""
        if segment in ("", "."):
            return
        current = nodes[-1]
        if not current.is_dir:
            raise VfsError("Not a directory")
        if segment == "..":
            if parts:
                parts.pop()
                nodes.pop()
            return
        child = current.children.get(segment)
        if child is None:
            raise VfsError("No such file or directory")
        parts.append(segment)
        nodes.append(child)


def iter_nodes(node):
    """Обойти поддерево, начиная с самого узла."""
    yield node
    for child in node.children.values():
        yield from iter_nodes(child)


def collect_stats(node, depth=0):
    """Вернуть (число каталогов, число файлов, глубина) поддерева.

    Глубина корня равна 0, его потомков — 1 и так далее.
    """
    if not node.is_dir:
        return 0, 1, depth
    dirs, files, deepest = 1, 0, depth
    for child in node.children.values():
        sub_dirs, sub_files, sub_depth = collect_stats(child, depth + 1)
        dirs += sub_dirs
        files += sub_files
        deepest = max(deepest, sub_depth)
    return dirs, files, deepest


def child_path(where, name):
    """Собрать путь потомка для сообщений об ошибках."""
    return where.rstrip("/") + "/" + name


def read_owner(raw, where):
    """Прочитать владельца и группу узла из описания."""
    names = []
    for key, default in (("owner", DEFAULT_OWNER), ("group", DEFAULT_GROUP)):
        value = raw.get(key, default)
        if not isinstance(value, str) or not is_valid_name(value):
            raise VfsLoadError(f"{where}: invalid {key} {value!r}")
        names.append(value)
    return names


def decode_content(raw, where):
    """Получить байты содержимого файла с учётом кодировки."""
    content = raw.get("content", "")
    encoding = raw.get("encoding", ENCODING_TEXT)
    if not isinstance(content, str):
        raise VfsLoadError(f"{where}: content must be a string")
    if encoding == ENCODING_TEXT:
        return content.encode("utf-8")
    if encoding != ENCODING_BASE64:
        raise VfsLoadError(f"{where}: unknown encoding {encoding!r}")
    try:
        return base64.b64decode(content, validate=True)
    except binascii.Error:
        raise VfsLoadError(f"{where}: invalid base64 data") from None


def build_file(raw, where):
    """Построить узел-файл по описанию."""
    owner, group = read_owner(raw, where)
    return Node(False, owner, group, data=decode_content(raw, where))


def build_dir(raw, where):
    """Построить узел-каталог со всеми потомками."""
    owner, group = read_owner(raw, where)
    items = raw.get("children", {})
    if not isinstance(items, dict):
        raise VfsLoadError(f"{where}: children must be an object")
    node = Node(True, owner, group)
    for name, item in items.items():
        if name in RESERVED_NAMES or "/" in name:
            raise VfsLoadError(f"{where}: invalid entry name {name!r}")
        node.children[name] = build_node(item, child_path(where, name))
    return node


def build_node(raw, where):
    """Построить узел VFS из разобранного JSON."""
    if not isinstance(raw, dict):
        raise VfsLoadError(f"{where}: node must be an object")
    kind = raw.get("type")
    if kind == TYPE_DIR:
        return build_dir(raw, where)
    if kind == TYPE_FILE:
        return build_file(raw, where)
    raise VfsLoadError(f"{where}: unknown node type {kind!r}")


def build_vfs(raw):
    """Построить VFS из разобранного JSON; корень должен быть каталогом."""
    root = build_node(raw, "/")
    if not root.is_dir:
        raise VfsLoadError("/: root must be a directory")
    return Vfs(root)


def default_vfs():
    """Создать VFS по умолчанию (в памяти, без файла)."""
    return build_vfs(DEFAULT_TREE)


def read_json(path):
    """Прочитать JSON-файл VFS; ошибки превращаются в VfsLoadError."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise VfsLoadError(f"VFS file not found: {path}") from None
    except OSError as error:
        raise VfsLoadError(f"cannot read {path}: {error.strerror}") from None
    except ValueError as error:
        raise VfsLoadError(f"invalid VFS format in {path}: {error}") from None


def load_vfs(path):
    """Загрузить VFS из JSON-файла целиком в память."""
    raw = read_json(path)
    try:
        return build_vfs(raw)
    except VfsLoadError as error:
        raise VfsLoadError(f"invalid VFS format in {path}: {error}") from None
