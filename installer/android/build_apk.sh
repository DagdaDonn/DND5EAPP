#!/bin/bash
set -e
# Run from the repo root regardless of where this script is invoked
# from -- same convention as installer/windows/build_exe.sh. This
# script lives two levels down, in installer/android/, so it takes two
# ".." to reach the repo root.
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
echo "=== MIMIC — Android APK Builder ==="
echo
echo "NOTE: untested in CI/sandboxes without a real Android SDK/NDK --"
echo "see packaging/android/BUILD_APK.md before running this for real."
echo

SPEC_FILE="packaging/android/pysidedeploy.spec"

echo "Step 1: Checking prerequisites..."
if [ -z "$ANDROID_SDK_ROOT" ]; then
    echo "ERROR: ANDROID_SDK_ROOT is not set." >&2
    echo "  Install the Android SDK and export ANDROID_SDK_ROOT to its path." >&2
    exit 1
fi
if [ -z "$ANDROID_NDK_ROOT" ]; then
    echo "ERROR: ANDROID_NDK_ROOT is not set." >&2
    echo "  Install the Qt-pinned NDK version and export ANDROID_NDK_ROOT to its path." >&2
    echo "  See packaging/android/README.md -- 'whatever's newest' is usually the wrong version." >&2
    exit 1
fi
if [ ! -f "$SPEC_FILE" ]; then
    echo "ERROR: $SPEC_FILE not found." >&2
    echo "  Generate it first with:" >&2
    echo "    pyside6-android-deploy --init --input-file dnd_app/ui_android/main.py" >&2
    echo "  then move the generated pysidedeploy.spec into packaging/android/" >&2
    echo "  and adjust it per packaging/android/README.md before retrying." >&2
    exit 1
fi
echo "  ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT"
echo "  ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT"
echo "  Spec file: $SPEC_FILE"

echo
echo "Step 2: Installing/upgrading PySide6..."
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade PySide6

echo
echo "Step 3: Verifying pyside6-android-deploy is available..."
if ! command -v pyside6-android-deploy >/dev/null 2>&1; then
    echo "ERROR: pyside6-android-deploy not found on PATH after installing PySide6." >&2
    echo "  Check your Python environment/venv is the one pip installed into." >&2
    exit 1
fi

echo
echo "Step 4: Running pyside6-android-deploy (this can take a while on a"
echo "first build -- it compiles a full python-for-android distribution,"
echo "not just freezes already-installed packages)..."
pyside6-android-deploy --config-file "$SPEC_FILE"

echo
echo "=== Done! ==="
echo "Look for the built .apk in the deploy tool's output directory"
echo "(reported above by pyside6-android-deploy itself -- its exact"
echo "location depends on the spec file's configured build directory)."
echo "This is a DEBUG-signed build. See packaging/android/BUILD_APK.md"
echo "for release signing before distributing it."
