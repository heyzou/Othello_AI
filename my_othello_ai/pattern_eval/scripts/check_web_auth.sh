#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERN_EVAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"
TOKEN_FILE="$PATTERN_EVAL_DIR/secrets/othellopy_token.env"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

cd "$PATTERN_EVAL_DIR"

if [[ -f "$TOKEN_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$TOKEN_FILE"
  set +a
fi

"$PYTHON_BIN" "$PATTERN_EVAL_DIR/web_automation/check_web_auth.py"
