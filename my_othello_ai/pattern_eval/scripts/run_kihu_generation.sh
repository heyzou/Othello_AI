#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_EVAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"
TEST_MODE=1

if [[ "${1:-}" == "-test" ]]; then
  TEST_MODE=1
  shift
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

PLAYER_FILE="${1:-players/current.py}"
TOTAL_GAMES="${2:-10}"

if [[ "$PLAYER_FILE" != */* ]]; then
  if [[ -f "$PATTERN_EVAL_DIR/players/$PLAYER_FILE" ]]; then
    PLAYER_FILE="players/$PLAYER_FILE"
  elif [[ -f "$PATTERN_EVAL_DIR/players/baselines/$PLAYER_FILE" ]]; then
    PLAYER_FILE="players/baselines/$PLAYER_FILE"
  elif [[ -f "$PATTERN_EVAL_DIR/players/experiments/$PLAYER_FILE" ]]; then
    PLAYER_FILE="players/experiments/$PLAYER_FILE"
  fi
fi

cd "$PATTERN_EVAL_DIR"

if ! "$PYTHON_BIN" -c "import othellopy" >/dev/null 2>&1; then
  echo "ERROR: othellopy is not installed. Install it first: pip install -U othellopy" >&2
  exit 1
fi

if [[ "$TEST_MODE" == "1" ]]; then
  echo "TEST MODE: move timeout disabled for kihu generation."
fi

MYPLAYER_FILE="$PLAYER_FILE" TOTAL_GAMES="$TOTAL_GAMES" MOVE_TIMEOUT_SECONDS=none "$PYTHON_BIN" "$PATTERN_EVAL_DIR/kihu_generation/run_kihu_generation_notebook.py"
