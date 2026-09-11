#!/usr/bin/env bash
set -euo pipefail

PROJECT="/mnt/c/Users/OBRIET/Dev/Projects/Extra/DND/DND5EAPP"
UI_DIR="$PROJECT/dnd_app/ui_android"
DIST_DIR="$PROJECT/dist"

echo "=== MIMIC Android build ==="
echo "Project: $PROJECT"

# Preconditions
if [[ ! -f "$UI_DIR/buildozer.spec" ]]; then
    echo "ERROR: buildozer.spec not found" >&2
    exit 1
fi

cd "$PROJECT"
if [[ ! -f shiboken6-6.11.2-6.11.2-cp311-cp311-android_aarch64.whl ]]; then
    echo "Copying wheels to repo root..."
    cp packaging/android/wheels/*.whl .
fi

cd "$UI_DIR"
if [[ ! -e .buildozer ]]; then
    echo "Creating .buildozer symlink to deployment/.buildozer..."
    ln -s ../../deployment/.buildozer .buildozer
fi

echo
echo "=== Running buildozer ==="
python3.11 -m buildozer android debug

APK=$(ls -t MIMIC-*.apk 2>/dev/null | head -n 1 || true)
if [[ -z "$APK" ]]; then
    echo "ERROR: no APK produced" >&2
    exit 1
fi

mkdir -p "$DIST_DIR"
mv -f "$APK" "$DIST_DIR/"

echo
echo "=== BUILD COMPLETE ==="
echo "APK: $DIST_DIR/$APK"
