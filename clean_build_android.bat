@echo off
REM Clean release build of the MIMIC APK: opens WSL in this window and runs
REM clean_build_android.sh (kills leftover build processes, clears previous
REM build outputs and staging, pre-flights p4a_hook.py, stages main.py +
REM dnd_app/, runs buildozer android release, converts the AAB to an APK).
REM Keeps the expensive compiled caches (libs/arm64-v8a, _python_bundle*,
REM other_builds) so this is not a 30-45 minute from-scratch rebuild.
REM
REM "%~dp0." rather than "%~dp0": the trailing backslash of %~dp0 would
REM escape the closing quote when wsl.exe parses its arguments.
title MIMIC clean Android build
for /f "usebackq delims=" %%P in (`wsl.exe wslpath -a "%~dp0."`) do set "WSL_PATH=%%P"
if not defined WSL_PATH (
    echo ERROR: could not resolve this folder to a WSL path - is WSL installed?
    pause
    exit /b 1
)
wsl.exe bash -lc "cd '%WSL_PATH%' && bash ./clean_build_android.sh"
if errorlevel 1 (
    echo.
    echo BUILD FAILED - scroll up, or see the /tmp/mimic-build-*.log path printed above.
) else (
    echo.
    echo Build finished.
)
pause
