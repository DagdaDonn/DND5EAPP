@echo off
setlocal enabledelayedexpansion
REM Run from the repo root regardless of where this script is invoked
REM from -- same convention as installer\windows\build_exe.bat. This
REM script lives two levels down, in installer\android\, so it takes
REM two ".." to reach the repo root.
cd /d "%~dp0..\.."
echo === MIMIC - Android APK Builder (Windows) ===
echo.
echo NOTE: untested in this sandbox -- there's no Android SDK/NDK here
echo to run against. pyside6-android-deploy has supported Windows as a
echo host OS since PySide6 6.5, but this script itself has only been
echo checked for correctness, not run against a real toolchain. See
echo packaging\android\BUILD_APK.md and packaging\android\README.md
echo before relying on it.
echo.

set SPEC_FILE=packaging\android\pysidedeploy.spec

echo [1/4] Checking prerequisites...
if "%ANDROID_SDK_ROOT%"=="" (
    echo ERROR: ANDROID_SDK_ROOT is not set.
    echo   Install the Android SDK and set ANDROID_SDK_ROOT to its path
    echo   ^(System Properties -^> Environment Variables, or "setx ANDROID_SDK_ROOT ..."^).
    pause & exit /b 1
)
if "%ANDROID_NDK_ROOT%"=="" (
    echo ERROR: ANDROID_NDK_ROOT is not set.
    echo   Install the Qt-pinned NDK version and set ANDROID_NDK_ROOT to its path.
    echo   See packaging\android\README.md -- "whatever's newest" is usually the wrong version.
    pause & exit /b 1
)
if not exist "%SPEC_FILE%" (
    echo ERROR: %SPEC_FILE% not found.
    echo   Generate it first with:
    echo     pyside6-android-deploy --init --input-file dnd_app\ui_android\main.py
    echo   then move the generated pysidedeploy.spec into packaging\android\
    echo   and adjust it per packaging\android\README.md before retrying.
    pause & exit /b 1
)
echo   ANDROID_SDK_ROOT=%ANDROID_SDK_ROOT%
echo   ANDROID_NDK_ROOT=%ANDROID_NDK_ROOT%
echo   Spec file: %SPEC_FILE%

echo.
echo [2/4] Installing/upgrading PySide6...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade PySide6 --quiet
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Make sure Python is in PATH.
    pause & exit /b 1
)

echo.
echo [3/4] Verifying pyside6-android-deploy is available...
where pyside6-android-deploy >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: pyside6-android-deploy not found on PATH after installing PySide6.
    echo   Check your Python environment/venv is the one pip installed into.
    pause & exit /b 1
)

echo.
echo [4/4] Running pyside6-android-deploy ^(this can take a while on a
echo first build -- it compiles a full python-for-android distribution,
echo not just freezes already-installed packages^)...
pyside6-android-deploy --config-file "%SPEC_FILE%"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed. See packaging\android\BUILD_APK.md's
    echo troubleshooting table for common causes ^(NDK version mismatch
    echo is the most frequent one^).
    pause & exit /b 1
)

echo.
echo === Done! ===
echo Look for the built .apk in the deploy tool's output directory
echo ^(reported above by pyside6-android-deploy itself -- its exact
echo location depends on the spec file's configured build directory^).
echo This is a DEBUG-signed build, fine for sideloading onto your own
echo phone via USB or a file transfer -- see packaging\android\BUILD_APK.md
echo for release signing if you ever need to distribute it more widely.
pause
