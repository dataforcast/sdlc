#!/usr/bin/env bash
# Launch both the backend and the frontend dev server in the background.
# Logs and PID files are written under .run/ so stop_app.sh can clean up.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
set -a
# shellcheck disable=SC1090
source "${ROOT_DIR}/.env"
set +a

RUN_DIR="${ROOT_DIR}/.run"
mkdir -p "${RUN_DIR}"

cd "${ROOT_DIR}/backend"
nohup uv run uvicorn app.main:app --host "${BACKEND_HOST}" --port "${BACKEND_PORT}" \
    > "${RUN_DIR}/backend.log" 2>&1 &
echo $! > "${RUN_DIR}/backend.pid"

READY=false
for _ in $(seq 1 50); do
    if curl --fail --silent "http://${BACKEND_HOST}:${BACKEND_PORT}/backend/health" > /dev/null; then
        READY=true
        break
    fi
    sleep 0.2
done

if [[ "${READY}" != "true" ]]; then
    echo "Backend did not become ready in time, see ${RUN_DIR}/backend.log" >&2
    exit 1
fi

cd "${ROOT_DIR}/frontend"
nohup pnpm dev -- --port "${FRONTEND_PORT}" \
    > "${RUN_DIR}/frontend.log" 2>&1 &
echo $! > "${RUN_DIR}/frontend.pid"

echo "Backend running at  http://${BACKEND_HOST}:${BACKEND_PORT}"
echo "Frontend running at http://localhost:${FRONTEND_PORT}"
echo "Stop with ./scripts/stop_app.sh"
