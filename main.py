#!/usr/bin/env python3
"""Android app entry point.

The Android clean build (packaging/android/clean_build_android.sh) copies
this file to the root of the APK's app folder; it only starts
dnd_app/ui_android/main.py, so the app's code stays in one place. Keep it
at the repo root, next to dnd_app/.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dnd_app.ui_android import main as _ui_main

if __name__ == "__main__":
    _ui_main.main()
