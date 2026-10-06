"""Команды эмулятора."""

from src.args import check_arg_count, split_flags
from src.errors import ShellError, ShellExit
from src.vfs import VfsError, collect_stats, is_valid_name, iter_nodes

EXIT_CODE_MASK = 0xFF
LS_FLAGS = "al"
FLAG_ALL = "a"
FLAG_LONG = "l"
CHOWN_FLAGS = "R"
FLAG_RECURSIVE = "R"
OWNER_WIDTH = 8
SIZE_WIDTH = 6
COLUMN_GAP = "  "


def find_node(shell, name, path):
    """Найти узел по пути; ошибку VFS превратить в ShellError.

    Возвращает кортеж (компоненты пути от корня, узел).
    """
    try:
        return shell.vfs.resolve(path, shell.cwd)
    except VfsError as error:
        raise ShellError(f"{name}: {path}: {error}") from None


def visible_entries(node, flags):
    """Вернуть отсортированные пары (имя, узел) каталога."""
    names = sorted(node.children)
    if FLAG_ALL not in flags:
        names = [name for name in names if not name.startswith(".")]
    return [(name, node.children[name]) for name in names]


def long_line(name, node):
    """Сформировать строку подробного вывода ls -l."""
    kind = "d" if node.is_dir else "-"
    return (
        f"{kind} {node.owner:<{OWNER_WIDTH}} {node.group:<{OWNER_WIDTH}} "
        f"{node.size:>{SIZE_WIDTH}} {name}"
    )


def render_entries(path, node, flags):
    """Показать содержимое каталога или сам файл."""
    entries = visible_entries(node, flags) if node.is_dir else [(path, node)]
    if FLAG_LONG in flags:
        return "\n".join(long_line(name, item) for name, item in entries)
    return COLUMN_GAP.join(name for name, _ in entries)


def cmd_ls(shell, args):
    """ls [-a] [-l] [ПУТЬ...]: показать содержимое каталогов VFS."""
    flags, paths = split_flags("ls", args, LS_FLAGS)
    targets = paths or ["."]
    titled = len(targets) > 1
    blocks = []
    for path in targets:
        _, node = find_node(shell, "ls", path)
        block = render_entries(path, node, flags)
        if titled and node.is_dir:
            block = f"{path}:\n{block}" if block else f"{path}:"
        blocks.append(block)
    return "\n\n".join(blocks)


def cmd_cd(shell, args):
    """cd [КАТАЛОГ]: сменить текущий каталог (без аргумента — корень)."""
    check_arg_count("cd", args, 0, 1)
    target = args[0] if args else "/"
    parts, node = find_node(shell, "cd", target)
    if not node.is_dir:
        raise ShellError(f"cd: {target}: Not a directory")
    shell.cwd = parts
    return None


def cmd_echo(shell, args):
    """echo [СТРОКА...]: вывести аргументы через пробел."""
    return " ".join(args)


def cmd_rev(shell, args):
    """rev ФАЙЛ...: вывести строки файлов, развернув каждую."""
    check_arg_count("rev", args, 1, None)
    lines = []
    for path in args:
        _, node = find_node(shell, "rev", path)
        if node.is_dir:
            raise ShellError(f"rev: {path}: Is a directory")
        text = node.data.decode("utf-8", errors="replace")
        lines.extend(line[::-1] for line in text.splitlines())
    return "\n".join(lines)


def parse_owner_spec(spec):
    """Разобрать ВЛАДЕЛЕЦ[:ГРУППА] в пару (владелец, группа).

    Отсутствующая часть заменяется на None (не меняется).
    """
    owner, _, group = spec.partition(":")
    names = [name for name in (owner, group) if name]
    valid = names and all(is_valid_name(name) for name in names)
    if not valid:
        raise ShellError(f"chown: invalid user: '{spec}'")
    return owner or None, group or None


def apply_owner(node, owner, group):
    """Изменить владельца и/или группу узла (только в памяти)."""
    if owner is not None:
        node.owner = owner
    if group is not None:
        node.group = group


def cmd_chown(shell, args):
    """chown [-R] ВЛАДЕЛЕЦ[:ГРУППА] ПУТЬ...: сменить владельца узлов."""
    flags, operands = split_flags("chown", args, CHOWN_FLAGS)
    check_arg_count("chown", operands, 2, None)
    owner, group = parse_owner_spec(operands[0])
    for path in operands[1:]:
        _, node = find_node(shell, "chown", path)
        targets = iter_nodes(node) if FLAG_RECURSIVE in flags else [node]
        for target in targets:
            apply_owner(target, owner, group)
    return None


def cmd_vfs_info(shell, args):
    """Служебная команда: статистика загруженной VFS."""
    check_arg_count("vfs-info", args, 0, 0)
    dirs, files, depth = collect_stats(shell.vfs.root)
    return f"directories: {dirs}\nfiles: {files}\nmax depth: {depth}"


def cmd_exit(shell, args):
    """Завершить работу эмулятора с необязательным кодом возврата."""
    check_arg_count("exit", args, 0, 1)
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError:
            raise ShellError("exit: numeric argument required") from None
    raise ShellExit(code & EXIT_CODE_MASK)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "echo": cmd_echo,
    "rev": cmd_rev,
    "chown": cmd_chown,
    "vfs-info": cmd_vfs_info,
    "exit": cmd_exit,
}
