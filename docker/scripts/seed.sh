#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

set -a
# shellcheck disable=SC1090
source "${ROOT_DIR}/.env.docker"
set +a

cd "${ROOT_DIR}/backend"
uv run python manage.py seed
