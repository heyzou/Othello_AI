#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYER_FILE="${1:-current.py}"
GAMES_PER_SIDE="${2:-100}"
PYTHON_BIN="${PYTHON:-python}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

if [[ "$PLAYER_FILE" != */* ]]; then
  if [[ -f "$SCRIPT_DIR/players/$PLAYER_FILE" ]]; then
    PLAYER_FILE="$SCRIPT_DIR/players/$PLAYER_FILE"
  elif [[ -f "$SCRIPT_DIR/players/baselines/$PLAYER_FILE" ]]; then
    PLAYER_FILE="$SCRIPT_DIR/players/baselines/$PLAYER_FILE"
  elif [[ -f "$SCRIPT_DIR/players/experiments/$PLAYER_FILE" ]]; then
    PLAYER_FILE="$SCRIPT_DIR/players/experiments/$PLAYER_FILE"
  else
    case "$PLAYER_FILE" in
      my_book_ab_add_hash.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_001_add_hash.py" ;;
      my_book_ab_weight_order.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_002_weight_order.py" ;;
      my_book_ab_weight_order_search_hash.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_003_weight_order_search_hash.py" ;;
      my_book_ab_strong_weight_search_hash.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_004_strong_weight_search_hash.py" ;;
      my_book_ab_qweight_search_hash.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_005_qweight_search_hash.py" ;;
      my_book_ab_precomputed_eval_search_hash.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_006_precomputed_eval_search_hash.py" ;;
      my_book_ab_precomputed_eval_addkey_cache.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_007_precomputed_eval_addkey_cache.py" ;;
      my_book_ab_no_eval_sort_endgame.py) PLAYER_FILE="$SCRIPT_DIR/players/experiments/exp_008_no_eval_sort_endgame.py" ;;
      *) PLAYER_FILE="$SCRIPT_DIR/players/$PLAYER_FILE" ;;
    esac
  fi
fi

cd "$SCRIPT_DIR"
MYPLAYER_FILE="$PLAYER_FILE" GAMES_PER_SIDE="$GAMES_PER_SIDE" "$PYTHON_BIN" run_common_notebook.py
