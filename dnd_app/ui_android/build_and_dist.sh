#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$SCRIPT_DIR"

echo "=== MIMIC Android build ==="
echo "Project root: $PROJECT_ROOT"
echo
echo "NOTE: first build of the day takes 20-40 minutes."
echo "Subsequent builds after only .py/.qml changes take under 2 minutes."
echo

python3.11 -m buildozer android debug

BIN_DIR="$SCRIPT_DIR/bin"
APK_PATH=""

if [ -d "$BIN_DIR" ]; then
    APK_PATH="$(ls -t "$BIN_DIR"/*.apk 2>/dev/null | head -1 || true)"
fi

if [ -z "$APK_PATH" ]; then
    echo "No APK in $BIN_DIR -- searching .buildozer/ instead..."
    APK_PATH="$(find "$SCRIPT_DIR/.buildozer" -name '*.apk' 2>/dev/null | xargs -r ls -t | head -1 || true)"
fi

if [ -z "$APK_PATH" ]; then
    echo "ERROR: no APK found in $BIN_DIR or under .buildozer/"
    exit 1
fi

mkdir -p "$PROJECT_ROOT/dist"
DEST="$PROJECT_ROOT/dist/MIMIC-0.1-arm64-v8a-debug.apk"
cp "$APK_PATH" "$DEST"

echo
echo "=== BUILD COMPLETE ==="
echo "APK: $DEST"
echo "Install with: adb install -r \"$DEST\""
