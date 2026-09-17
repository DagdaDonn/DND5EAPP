#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/dnd_app/ui_android/build_and_dist.sh" "$@"
