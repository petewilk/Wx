#!/usr/bin/env bash
# Upload the Wx HTML apps to petewilk.com.
#
# Usage: ./deploy.sh [-n]    (-n = dry run, show what would be sent)
#
# Copies only the git-tracked top-level *.html files. The web root also holds
# WordPress, so never sync the whole directory or use --delete here.
set -euo pipefail

HOST="${WX_DEPLOY_HOST:-dreamhost}"           # alias from ~/.ssh/config
DEST="${WX_DEPLOY_DEST:-petewilk.com/}"       # relative to the remote home dir

cd "$(dirname "$0")"

DRY_RUN=()
[[ "${1:-}" == "-n" ]] && DRY_RUN=(-n)

BRANCH="$(git branch --show-current)"
if [[ "$BRANCH" != "main" ]]; then
  echo "Refusing to deploy from '${BRANCH:-detached HEAD}'; check out main first." >&2
  exit 1
fi

FILES=()
while IFS= read -r f; do FILES+=("$f"); done < <(git ls-files -- '*.html' ':!:*/*')
if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No HTML files to deploy." >&2
  exit 1
fi

if ! git diff --quiet HEAD -- "${FILES[@]}"; then
  echo "Warning: uncommitted changes in files being deployed:" >&2
  git diff --stat HEAD -- "${FILES[@]}" >&2
fi

echo "Deploying to $HOST:$DEST (branch $BRANCH, $(git rev-parse --short HEAD))"
rsync -tvz ${DRY_RUN[@]+"${DRY_RUN[@]}"} -- "${FILES[@]}" "$HOST:$DEST"
