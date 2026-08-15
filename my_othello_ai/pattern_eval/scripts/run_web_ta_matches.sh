#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_EVAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"
TOKEN_FILE="$PATTERN_EVAL_DIR/secrets/othellopy_token.env"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

MY_PLAYER_ID="${1:-}"
GAMES="${2:-2}"

if [[ -z "$MY_PLAYER_ID" ]]; then
  echo "Usage: OTHELLOPY_AUTH_TOKEN=... bash $0 <your_web_player_id> [games]" >&2
  exit 2
fi

cd "$PATTERN_EVAL_DIR"

if [[ -f "$TOKEN_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$TOKEN_FILE"
  set +a
fi

"$PYTHON_BIN" "$PATTERN_EVAL_DIR/web_automation/create_web_matches.py" \
  --my-player-id "$MY_PLAYER_ID" \
  --opponent-id "qZ61Xg3cdvQevP66EEVq" \
  --games "$GAMES" \
  --wait
