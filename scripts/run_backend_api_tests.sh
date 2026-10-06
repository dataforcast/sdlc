#!/usr/bin/env bash
# Start the real backend, wait for readiness, run backend API tests, then stop it.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
set -a
# shellcheck disable=SC1090
source "${ROOT_DIR}/.env"
set +a

BACKEND_PID=""

cleanup() {
    if [[ -n "${BACKEND_PID}" ]]; then
        kill "${BACKEND_PID}" 2>/dev/null || true
        wait "${BACKEND_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

cd "${ROOT_DIR}/backend"

uv run uvicorn app.main:app --host "${BACKEND_HOST}" --port "${BACKEND_PORT}" &
BACKEND_PID=$!

READY=false
for _ in $(seq 1 50); do
    if curl --fail --silent "http://${BACKEND_HOST}:${BACKEND_PORT}/backend/health" > /dev/null; then
        READY=true
        break
    fi
    sleep 0.2
done

if [[ "${READY}" != "true" ]]; then
    echo "Backend did not become ready in time" >&2
    exit 1
fi

uv run pytest tests/api "$@"
