#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
APP_VERSION="$(sed -nE 's/^version[[:space:]]*=[[:space:]]*//p' "$ROOT/dnd_app/ui_android/buildozer.spec" | head -1)"
APK="$ROOT/dist/MIMIC-${APP_VERSION:-unknown}-arm64-v8a-debug.apk"
[ -f "$APK" ] || { echo "No APK at $APK — run build_android.sh first"; exit 1; }
adb uninstall org.mimic.mimic 2>/dev/null || true
adb install -r "$APK"
echo "Installed. Launch MIMIC on the phone."
