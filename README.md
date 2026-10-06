# Эмулятор языка оболочки ОС (вариант 2)

## Общее описание

Консольный эмулятор оболочки UNIX-подобной ОС на Python 3 (только
стандартная библиотека). Приглашение к вводу строится из реальных данных
ОС: `username@hostname:~$`.

## Состояние (этапы 1–3: REPL, конфигурация, VFS)

Реализовано:

- консольный диалог (REPL) с приглашением из имени пользователя и
  хоста реальной ОС;
- парсер: ввод делится на команду и аргументы по пробелам;
- сообщения об ошибках: неизвестная команда, неверные аргументы;
- команды-заглушки `ls` и `cd` печатают своё имя и аргументы;
- `exit [код]` завершает работу; Ctrl-D (EOF) тоже завершает работу.

### Параметры командной строки (этап 2)

| Параметр | Описание |
|----------|----------|
| `--vfs PATH` | путь к JSON-файлу с VFS (если не указан — VFS по умолчанию в памяти) |
| `--script PATH` | путь к стартовому скрипту |

При запуске все заданные параметры выводятся в виде отладочных строк
`[debug] ...`.

Стартовый скрипт — текстовый файл (UTF-8), по одной команде в строке.
Команды выполняются последовательно; на экране виден и ввод (с
приглашением), и вывод, как в диалоге с пользователем. Пустые строки
пропускаются, ошибочные строки пропускаются с сообщением
`script: PATH: line N: skipped (error)`. После скрипта запускается
обычный REPL (если скрипт не вызвал `exit`). Если файл скрипта не найден
или нечитаем, выводится ошибка и эмулятор завершается с кодом 1.

## Сборка и запуск тестов

Сборка не нужна. Требуется Python 3.8+.

```
./run.sh            # или: make run, или: python3 -m src
make test           # или: python3 -m unittest discover -s tests -t .
```

### Виртуальная файловая система (этап 3)

Вся VFS хранится в памяти; на диск ничего не распаковывается и не
записывается. Источник — JSON-файл. Корень — каталог:

```json
{
  "type": "dir",
  "owner": "root",
  "group": "root",
  "children": {
    "a.txt": {"type": "file", "content": "text\n"},
    "b.bin": {"type": "file", "encoding": "base64", "content": "AAEC"}
  }
}
```

- `type`: `dir` или `file` (обязательно);
- `owner`, `group` — необязательны, по умолчанию `root`;
- у файла `content` (строка) и `encoding`: `utf-8` (по умолчанию)
  или `base64` для двоичных данных;
- у каталога `children` — объект «имя → узел».

Ошибки загрузки (файл не найден, неверный JSON, неверная структура или
base64) выводятся как `emulator: ...`, код возврата 1.

Служебная команда `vfs-info` печатает число каталогов, файлов и
максимальную глубину вложенности загруженной VFS.

## Структура

- `src/` — исходный код, `tests/` — тесты.
- `run.sh`, `Makefile` — запуск и тесты.
- `tests/emu/` — стартовые скрипты эмулятора (`*.esh`).
- `tests/vfs/` — образцы VFS (минимальная, несколько файлов, 4 уровня,
  base64, некорректные).
- `tests/scripts/` — скрипты реальной ОС (sh), вызывающие эмулятор.

Скрипт реальной ОС для проверки всех параметров этапа 2:
`sh tests/scripts/stage2_params.sh`.
Скрипт для разных вариантов VFS: `sh tests/scripts/stage3_vfs.sh`.

## Пример интерактивного сеанса

```
root@vm:~$ ls -l /tmp
ls: args=['-l', '/tmp']
root@vm:~$ cd docs
cd: args=['docs']
root@vm:~$ cd a b
cd: too many arguments
root@vm:~$ foo
foo: command not found
root@vm:~$ exit abc
exit: numeric argument required
root@vm:~$ exit 3
```

## Пример запуска со стартовым скриптом (этап 2)

```
$ python3 -m src --script tests/emu/stage2_errors.esh < /dev/null
[debug] emulator parameters:
[debug]   --vfs    = (not set)
[debug]   --script = tests/emu/stage2_errors.esh
root@vm:~$ ls -l /tmp
ls: args=['-l', '/tmp']
root@vm:~$ foo bar
foo: command not found
script: tests/emu/stage2_errors.esh: line 4: skipped (error)
root@vm:~$ exit 0
```

## Пример: VFS и ошибки загрузки (этап 3)

```
$ python3 -m src --vfs tests/vfs/deep.json --script tests/emu/stage3_all.esh < /dev/null
...
root@vm:~$ vfs-info
directories: 5
files: 6
max depth: 4

$ python3 -m src --vfs tests/vfs/missing.json
emulator: VFS file not found: tests/vfs/missing.json
```
