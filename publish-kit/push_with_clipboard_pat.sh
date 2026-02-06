#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./publish-kit/push_with_clipboard_pat.sh <github_username> [remote_name]
# Reads PAT from macOS clipboard and pushes current repo.

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <github_username> [remote_name]"
  exit 1
fi

USER_NAME="$1"
REMOTE_NAME="${2:-origin}"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

TOKEN="$(pbpaste | tr -d '\r\n')"
if [[ ! "$TOKEN" =~ ^(github_pat_|ghp_)[A-Za-z0-9_]+$ ]]; then
  echo "Clipboard does not look like a GitHub PAT (github_pat_... or ghp_...)"
  exit 2
fi

ASKPASS_FILE="$(mktemp)"
cleanup() {
  rm -f "$ASKPASS_FILE"
  unset GITHUB_TOKEN || true
}
trap cleanup EXIT

cat > "$ASKPASS_FILE" <<'AP'
#!/bin/sh
case "$1" in
  *Username*) echo "$GITHUB_USERNAME" ;;
  *Password*) echo "$GITHUB_TOKEN" ;;
  *) echo "" ;;
esac
AP
chmod +x "$ASKPASS_FILE"

export GITHUB_USERNAME="$USER_NAME"
export GITHUB_TOKEN="$TOKEN"
export GIT_ASKPASS="$ASKPASS_FILE"
export GIT_TERMINAL_PROMPT=0

git config http.version HTTP/1.1
git push -u "$REMOTE_NAME" main

echo "Push succeeded."
