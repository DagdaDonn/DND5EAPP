@echo off
REM Portable version, same pattern as build_android.bat: resolves this
REM script's own directory to a WSL path via wslpath rather than
REM hardcoding it.
for /f "usebackq delims=" %%P in (`wsl.exe wslpath -a "%~dp0"`) do set "WSL_PATH=%%P"
wsl.exe bash -lc "cd '%WSL_PATH%' && ./install_android.sh"
pause
