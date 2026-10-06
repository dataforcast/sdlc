#!/usr/bin/env bash
# Run backend unit tests (no server required).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT_DIR}/backend"

uv run pytest tests/unit "$@"
