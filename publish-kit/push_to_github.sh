#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./publish-kit/push_to_github.sh https://github.com/<username>/<repo>.git

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <github_repo_url>"
  exit 1
fi

REPO_URL="$1"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

git rev-parse --is-inside-work-tree >/dev/null

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git branch -M main
git push -u origin main

echo "Done. Remote: $REPO_URL"
