#!/usr/bin/env sh
cd "$(dirname "$0")/../.." || exit 1
python3 -m src --vfs tests/vfs/deep.json \
    --script tests/emu/stage5_chown.esh < /dev/null
