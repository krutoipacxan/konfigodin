#!/usr/bin/env sh
cd "$(dirname "$0")/../.." || exit 1
EMU="python3 -m src"
SCRIPT="tests/emu/stage3_all.esh"

for name in minimal files deep binary; do
    echo "=== VFS: tests/vfs/$name.json ==="
    $EMU --vfs "tests/vfs/$name.json" --script "$SCRIPT" < /dev/null
done

echo "=== VFS по умолчанию (параметр --vfs не указан) ==="
$EMU --script "$SCRIPT" < /dev/null

for name in missing invalid_json invalid_node invalid_base64; do
    echo "=== Ошибка загрузки: tests/vfs/$name.json ==="
    $EMU --vfs "tests/vfs/$name.json" < /dev/null
    echo "exit code: $?"
done
