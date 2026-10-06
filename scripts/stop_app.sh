#!/usr/bin/env bash
# Stop the backend and frontend processes started by start_app.sh.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/.run"

stop_pid_file() {
    local pid_file="$1"
    local label="$2"

    if [[ -f "${pid_file}" ]]; then
        local pid
        pid="$(cat "${pid_file}")"
        if kill "${pid}" 2>/dev/null; then
            wait "${pid}" 2>/dev/null || true
            echo "Stopped ${label} (pid ${pid})"
        else
            echo "${label} (pid ${pid}) was not running"
        fi
        rm -f "${pid_file}"
    else
        echo "No PID file for ${label}, nothing to stop"
    fi
}

stop_pid_file "${RUN_DIR}/backend.pid" "backend"
stop_pid_file "${RUN_DIR}/frontend.pid" "frontend"
