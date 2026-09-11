@echo off
setlocal
REM ============================================================
REM  MIMIC Android APK build
REM  Runs buildozer inside WSL. Produces dist\MIMIC-*.apk
REM ============================================================

set "PROJECT_WIN=C:\Users\OBRIET\Dev\Projects\Extra\DND\DND5EAPP"
set "PROJECT_WSL=/mnt/c/Users/OBRIET/Dev/Projects/Extra/DND/DND5EAPP"

echo.
echo === MIMIC Android build ===
echo Project: %PROJECT_WIN%
echo.

if not exist "%PROJECT_WIN%\dnd_app\ui_android\buildozer.spec" (
    echo ERROR: buildozer.spec not found at:
    echo   %PROJECT_WIN%\dnd_app\ui_android\buildozer.spec
    echo Check PROJECT_WIN in this script.
    exit /b 1
)

echo === Ensuring build environment ===
wsl.exe bash -lc "set -e; cd '%PROJECT_WSL%'; if [ ! -f shiboken6-6.11.2-6.11.2-cp311-cp311-android_aarch64.whl ]; then cp packaging/android/wheels/*.whl .; fi; cd dnd_app/ui_android; if [ ! -e .buildozer ]; then ln -s ../../deployment/.buildozer .buildozer; fi"
if errorlevel 1 (
    echo ERROR: failed to prepare build environment
    exit /b 1
)

echo.
echo === Running buildozer ===
wsl.exe bash -lc "set -e; cd '%PROJECT_WSL%/dnd_app/ui_android'; python3.11 -m buildozer android debug"
if errorlevel 1 (
    echo.
    echo === BUILD FAILED ===
    exit /b 1
)

echo.
echo === Locating APK ===
set "APK_NAME="
for /f "delims=" %%F in ('dir /b /o-d "%PROJECT_WIN%\dnd_app\ui_android\MIMIC-*.apk" 2^>nul') do (
    set "APK_NAME=%%F"
    goto :found
)
echo ERROR: no APK found in dnd_app\ui_android\
exit /b 1

:found
echo Found: %APK_NAME%
if not exist "%PROJECT_WIN%\dist" mkdir "%PROJECT_WIN%\dist"
move /y "%PROJECT_WIN%\dnd_app\ui_android\%APK_NAME%" "%PROJECT_WIN%\dist\" >nul

echo.
echo === BUILD COMPLETE ===
echo APK: %PROJECT_WIN%\dist\%APK_NAME%
echo.
echo Install on phone with:
echo   adb install -r "%PROJECT_WIN%\dist\%APK_NAME%"
echo.

endlocal
