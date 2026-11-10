#!/usr/bin/env bash
# Upload the Wx HTML apps to petewilk.com.
#
# Usage: ./deploy.sh [-n]    (-n = dry run, show what would be sent)
#
# Copies only git-tracked files, in this order so a page never loads before what it needs:
#   1. data/avy/**/*.json day files (everything except index.json), paths kept (rsync -R)
#   2. data/avy/**/index.json files
#   3. top-level *.js, then top-level *.html
# The web root also holds WordPress, so never sync the whole directory or use --delete here.
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
while IFS= read -r f; do FILES+=("$f"); done < <(git ls-files -- '*.js' ':!:*/*')
while IFS= read -r f; do FILES+=("$f"); done < <(git ls-files -- '*.html' ':!:*/*')
if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No HTML/JS files to deploy." >&2
  exit 1
fi

DAY_FILES=()
while IFS= read -r f; do DAY_FILES+=("$f"); done < <(git ls-files -- 'data/avy/**/*.json' ':!:data/avy/**/index.json')
INDEX_FILES=()
while IFS= read -r f; do INDEX_FILES+=("$f"); done < <(git ls-files -- 'data/avy/**/index.json')

if ! git diff --quiet HEAD -- "${FILES[@]}" ${DAY_FILES[@]+"${DAY_FILES[@]}"} ${INDEX_FILES[@]+"${INDEX_FILES[@]}"}; then
  echo "Warning: uncommitted changes in files being deployed:" >&2
  git diff --stat HEAD -- "${FILES[@]}" ${DAY_FILES[@]+"${DAY_FILES[@]}"} ${INDEX_FILES[@]+"${INDEX_FILES[@]}"} >&2
fi

echo "Deploying to $HOST:$DEST (branch $BRANCH, $(git rev-parse --short HEAD))"
if [[ ${#DAY_FILES[@]} -gt 0 ]]; then
  rsync -tvzR ${DRY_RUN[@]+"${DRY_RUN[@]}"} -- "${DAY_FILES[@]}" "$HOST:$DEST"
fi
if [[ ${#INDEX_FILES[@]} -gt 0 ]]; then
  rsync -tvzR ${DRY_RUN[@]+"${DRY_RUN[@]}"} -- "${INDEX_FILES[@]}" "$HOST:$DEST"
fi
rsync -tvz ${DRY_RUN[@]+"${DRY_RUN[@]}"} -- "${FILES[@]}" "$HOST:$DEST"
