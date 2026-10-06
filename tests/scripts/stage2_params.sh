#!/usr/bin/env sh
cd "$(dirname "$0")/../.." || exit 1
EMU="python3 -m src"

echo "=== 1. Без параметров (REPL получает EOF) ==="
$EMU < /dev/null

echo "=== 2. Только --script ==="
$EMU --script tests/emu/stage2_errors.esh < /dev/null
echo "exit code: $?"

echo "=== 3. Только --vfs (файл пока не читается) ==="
$EMU --vfs tests/vfs/any.json < /dev/null

echo "=== 4. Оба параметра ==="
$EMU --vfs tests/vfs/any.json --script tests/emu/stage2_no_exit.esh \
    < /dev/null

echo "=== 5. Несуществующий скрипт ==="
$EMU --script tests/emu/missing.esh < /dev/null
echo "exit code: $?"

echo "=== 6. Неизвестный параметр ==="
$EMU --bogus < /dev/null
echo "exit code: $?"
