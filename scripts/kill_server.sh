#!/usr/bin/env bash
# Free whatever process is bound to $BACKEND_PORT, for quick dev-loop recovery.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
set -a
# shellcheck disable=SC1090
source "${ROOT_DIR}/.env"
set +a

PIDS="$(lsof -ti ":${BACKEND_PORT}" 2>/dev/null || true)"

if [[ -n "${PIDS}" ]]; then
    echo "Killing process(es) on port ${BACKEND_PORT}: ${PIDS}"
    # shellcheck disable=SC2086
    kill ${PIDS}
else
    echo "No process found on port ${BACKEND_PORT}"
fi
