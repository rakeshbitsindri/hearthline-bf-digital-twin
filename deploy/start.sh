#!/usr/bin/env bash
# Launch the FastAPI engine (internal) and the Next.js UI (public $PORT) in one container.
# The UI proxies /twin-api to the engine, so the browser uses a single origin.
set -euo pipefail

PUBLIC_PORT="${PORT:-7860}"
API_PORT="8011"

echo "[hearthline] starting FastAPI engine on 127.0.0.1:${API_PORT}"
cd /srv/apps/api
uvicorn main:app --host 127.0.0.1 --port "${API_PORT}" &
API_PID=$!

# Wait for the engine to answer before exposing the UI, so the first page load has data.
for i in $(seq 1 60); do
  if python3 -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:${API_PORT}/health', timeout=2)" 2>/dev/null; then
    echo "[hearthline] engine is healthy"
    break
  fi
  sleep 1
done

echo "[hearthline] starting Next.js UI on 0.0.0.0:${PUBLIC_PORT}"
cd /srv/apps/web
export TWIN_API_ORIGIN="http://127.0.0.1:${API_PORT}"
node node_modules/next/dist/bin/next start -H 0.0.0.0 -p "${PUBLIC_PORT}" &
WEB_PID=$!

# If either process exits, stop the container so the host can restart it.
wait -n "${API_PID}" "${WEB_PID}"
echo "[hearthline] a process exited; shutting down"
kill "${API_PID}" "${WEB_PID}" 2>/dev/null || true
exit 1
