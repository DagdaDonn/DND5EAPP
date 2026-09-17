@echo off
REM Portable version: resolves this script's own directory to a WSL path
REM via wslpath, rather than hardcoding it -- matches how
REM packaging\android\setup_buildozer_spec.bat resolves its own root.
for /f "usebackq delims=" %%P in (`wsl.exe wslpath -a "%~dp0"`) do set "WSL_PATH=%%P"
wsl.exe bash -lc "cd '%WSL_PATH%' && ./build_android.sh"
pause
