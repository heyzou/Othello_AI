#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

cd "$SCRIPT_DIR"

mkdir -p models

echo "compile evaluate.out"
g++ -O2 -std=c++17 calc_additional_params.cpp -o evaluate.out

echo "train pattern weights"
"$PYTHON_BIN" reference_original_tensorflow_code.py
