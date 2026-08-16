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

MY_PLAYER_FILE="${1:-players/current.py}"
OPPONENT_PLAYER="${2:-AdvancedPlayer}"
TOTAL_GAMES="${3:-10}"

resolve_player_file() {
  local player_file="$1"
  if [[ "$player_file" != */* ]]; then
    if [[ -f "$PATTERN_EVAL_DIR/players/$player_file" ]]; then
      player_file="players/$player_file"
    elif [[ -f "$PATTERN_EVAL_DIR/players/baselines/$player_file" ]]; then
      player_file="players/baselines/$player_file"
    elif [[ -f "$PATTERN_EVAL_DIR/players/experiments/$player_file" ]]; then
      player_file="players/experiments/$player_file"
    elif [[ -f "$PATTERN_EVAL_DIR/players/random_opening/$player_file" ]]; then
      player_file="players/random_opening/$player_file"
    fi
  fi
  printf '%s\n' "$player_file"
}

MY_PLAYER_FILE="$(resolve_player_file "$MY_PLAYER_FILE")"
OPPONENT_PLAYER="$(resolve_player_file "$OPPONENT_PLAYER")"

cd "$PATTERN_EVAL_DIR"

if ! "$PYTHON_BIN" -c "import othellopy" >/dev/null 2>&1; then
  echo "ERROR: othellopy is not installed. Install it first: pip install -U othellopy" >&2
  exit 1
fi

if [[ "$TEST_MODE" == "1" ]]; then
  echo "TEST MODE: move timeout disabled for kihu generation."
fi

MYPLAYER_FILE="$MY_PLAYER_FILE" \
OPPONENT_PLAYER="$OPPONENT_PLAYER" \
TOTAL_GAMES="$TOTAL_GAMES" \
MOVE_TIMEOUT_SECONDS=none \
"$PYTHON_BIN" "$PATTERN_EVAL_DIR/kihu_generation/run_kihu_generation_notebook.py"
