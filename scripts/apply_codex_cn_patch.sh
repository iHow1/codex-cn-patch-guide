#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_PATH="${1:-$HOME/Applications/Codex.app}"

python3 "$ROOT_DIR/scripts/apply_codex_cn_patch.py" \
  --app "$APP_PATH" \
  --map "$ROOT_DIR/patches/codex_5_3_cn_patch.json"
