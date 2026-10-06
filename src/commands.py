"""Команды эмулятора (ls и cd пока заглушки)."""

from src.args import check_arg_count
from src.errors import ShellError, ShellExit
from src.vfs import collect_stats

EXIT_CODE_MASK = 0xFF


def stub_output(name, args):
    """Сформировать вывод заглушки: имя команды и её аргументы."""
    return f"{name}: args={args}"


def cmd_ls(shell, args):
    """Заглушка ls: печатает своё имя и аргументы."""
    return stub_output("ls", args)


def cmd_cd(shell, args):
    """Заглушка cd: печатает своё имя и аргументы."""
    check_arg_count("cd", args, 0, 1)
    return stub_output("cd", args)


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


def cmd_vfs_info(shell, args):
    """Служебная команда: статистика загруженной VFS."""
    check_arg_count("vfs-info", args, 0, 0)
    dirs, files, depth = collect_stats(shell.vfs.root)
    return f"directories: {dirs}\nfiles: {files}\nmax depth: {depth}"


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "vfs-info": cmd_vfs_info,
    "exit": cmd_exit,
}
