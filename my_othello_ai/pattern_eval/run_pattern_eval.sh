#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYER_FILE="${1:-my_book.py}"
GAMES_PER_SIDE="${2:-100}"
PYTHON_BIN="${PYTHON:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

if [[ "$PLAYER_FILE" != */* ]]; then
  PLAYER_FILE="$SCRIPT_DIR/players/$PLAYER_FILE"
fi

cd "$SCRIPT_DIR"
MYPLAYER_FILE="$PLAYER_FILE" GAMES_PER_SIDE="$GAMES_PER_SIDE" "$PYTHON_BIN" run_common_notebook.py
