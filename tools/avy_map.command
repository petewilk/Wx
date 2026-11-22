#!/bin/zsh
# Double-click launcher for the local avalanche rose map (macOS).
# Refreshes forecasts from the UAC emails, makes sure a local web server is
# running on port 8765, then opens the map in the default browser.
# A Desktop symlink to this file works the same as running it here.

PORT=8765
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Resolve the repo from this script's real location (follows the Desktop symlink).
SCRIPT="${0:A}"
REPO="${SCRIPT:h:h}"
cd "$REPO" || { echo "Repo not found at $REPO"; read -k1 "?Press any key to close."; exit 1; }

echo "Refreshing avalanche forecasts from email..."
python3 -I tools/fetch_uac_roses.py
STATUS=$?

if ! lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Starting local web server on port $PORT..."
  nohup python3 -m http.server $PORT --bind 127.0.0.1 >/dev/null 2>&1 &
  disown
  sleep 1
fi

open "http://localhost:$PORT/avy_map.html"

if [[ $STATUS -ne 0 ]]; then
  echo
  read -k1 "?The refresh reported a problem (see above). Press any key to close."
else
  echo "Done. You can close this window."
fi
