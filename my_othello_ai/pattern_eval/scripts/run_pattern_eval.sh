#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_EVAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_MODE=0

if [[ "${1:-}" == "-test" ]]; then
  TEST_MODE=1
  shift
fi

PLAYER_FILE="${1:-current.py}"
GAMES_PER_SIDE="${2:-100}"
PYTHON_BIN="${PYTHON:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

if [[ "$PLAYER_FILE" != */* ]]; then
  if [[ -f "$PATTERN_EVAL_DIR/players/$PLAYER_FILE" ]]; then
    PLAYER_FILE="$PATTERN_EVAL_DIR/players/$PLAYER_FILE"
  elif [[ -f "$PATTERN_EVAL_DIR/players/baselines/$PLAYER_FILE" ]]; then
    PLAYER_FILE="$PATTERN_EVAL_DIR/players/baselines/$PLAYER_FILE"
  elif [[ -f "$PATTERN_EVAL_DIR/players/experiments/$PLAYER_FILE" ]]; then
    PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/$PLAYER_FILE"
  elif find "$PATTERN_EVAL_DIR/players/experiments" -name "$PLAYER_FILE" -print -quit 2>/dev/null | grep -q .; then
    PLAYER_FILE="$(find "$PATTERN_EVAL_DIR/players/experiments" -name "$PLAYER_FILE" -print -quit)"
  else
    case "$PLAYER_FILE" in
      my_book_ab_add_hash.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_001_add_hash.py" ;;
      my_book_ab_weight_order.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_002_weight_order.py" ;;
      my_book_ab_weight_order_search_hash.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_003_weight_order_search_hash.py" ;;
      my_book_ab_strong_weight_search_hash.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_004_strong_weight_search_hash.py" ;;
      my_book_ab_qweight_search_hash.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_005_qweight_search_hash.py" ;;
      my_book_ab_precomputed_eval_search_hash.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_006_precomputed_eval_search_hash.py" ;;
      my_book_ab_precomputed_eval_addkey_cache.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_007_precomputed_eval_addkey_cache.py" ;;
      my_book_ab_no_eval_sort_endgame.py) PLAYER_FILE="$PATTERN_EVAL_DIR/players/experiments/exp_008_no_eval_sort_endgame.py" ;;
      *) PLAYER_FILE="$PATTERN_EVAL_DIR/players/$PLAYER_FILE" ;;
    esac
  fi
fi

cd "$PATTERN_EVAL_DIR"
if [[ "$TEST_MODE" == "1" ]]; then
  echo "TEST MODE: move timeout disabled; moves over 2.0 seconds will continue."
  MYPLAYER_FILE="$PLAYER_FILE" GAMES_PER_SIDE="$GAMES_PER_SIDE" MOVE_TIMEOUT_SECONDS=none "$PYTHON_BIN" run_common_notebook.py
else
  MYPLAYER_FILE="$PLAYER_FILE" GAMES_PER_SIDE="$GAMES_PER_SIDE" "$PYTHON_BIN" run_common_notebook.py
fi
