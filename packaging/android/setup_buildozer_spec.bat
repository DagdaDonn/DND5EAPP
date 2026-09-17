@echo off
setlocal enabledelayedexpansion

REM ==========================================================================
REM  MIMIC — buildozer.spec setup for Windows users
REM
REM  Lives at: packaging\android\setup_buildozer_spec.bat
REM
REM  One-time setup after cloning. Searches for Python 3.11, Android SDK,
REM  Android NDK, PySide6/Shiboken6 wheels, and Qt Android jars. Downloads
REM  or extracts what's missing. Rewrites the path lines in buildozer.spec.
REM
REM  Idempotent: safe to re-run. Backs up the spec before modifying.
REM ==========================================================================

REM ---------------------------------------------------------------------------
REM  Resolve project paths
REM ---------------------------------------------------------------------------
set "PROJECT_WIN=%~dp0..\.."
pushd "%PROJECT_WIN%"
set "PROJECT_WIN=%CD%"
popd

set "DRIVE=%PROJECT_WIN:~0,1%"
set "REST=%PROJECT_WIN:~2%"
set "REST=%REST:\=/%"
set "PROJECT_WSL=/mnt/%DRIVE%%REST%"

set "SPEC_WIN=%PROJECT_WIN%\dnd_app\ui_android\buildozer.spec"
set "SPEC_WSL=%PROJECT_WSL%/dnd_app/ui_android/buildozer.spec"
set "WHEELS_WIN=%PROJECT_WIN%\packaging\android\wheels"
set "WHEELS_WSL=%PROJECT_WSL%/packaging/android/wheels"
set "JARS_WIN=%PROJECT_WIN%\packaging\android\jars"
set "JARS_WSL=%PROJECT_WSL%/packaging/android/jars"

REM Wheel version + tags. Change here if upgrading.
set "PYSIDE_VER=6.11.2"
set "PY_TAG=cp311"
set "ARCH_TAG=android_aarch64"
set "PYSIDE_FILE_LOWER=pyside6-%PYSIDE_VER%-%PYSIDE_VER%-%PY_TAG%-%PY_TAG%-%ARCH_TAG%.whl"
set "PYSIDE_FILE_UPPER=PySide6-%PYSIDE_VER%-%PYSIDE_VER%-%PY_TAG%-%PY_TAG%-%ARCH_TAG%.whl"
set "SHIB_FILE=shiboken6-%PYSIDE_VER%-%PYSIDE_VER%-%PY_TAG%-%PY_TAG%-%ARCH_TAG%.whl"
set "PYSIDE_URL=https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-%PYSIDE_VER%-%PYSIDE_VER%-%PY_TAG%-%PY_TAG%-%ARCH_TAG%.whl"
set "SHIB_URL=https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-%PYSIDE_VER%-%PYSIDE_VER%-%PY_TAG%-%PY_TAG%-%ARCH_TAG%.whl"

echo.
echo === MIMIC buildozer.spec setup ===
echo Project (Windows): %PROJECT_WIN%
echo Project (WSL):     %PROJECT_WSL%
echo Spec file:         %SPEC_WIN%
echo.

if not exist "%SPEC_WIN%" (
    echo ERROR: buildozer.spec not found at:
    echo   %SPEC_WIN%
    echo Expected repo layout: DND5EAPP\dnd_app\ui_android\buildozer.spec
    exit /b 1
)

REM ---------------------------------------------------------------------------
REM  0. Verify WSL and Python 3.11
REM ---------------------------------------------------------------------------
echo [0/6] Checking WSL Python 3.11...

for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "command -v python3.11 >/dev/null 2>&1 && python3.11 --version 2>/dev/null | awk '{print $2}'"`) do (
    set "PY_VER=%%P"
)
if not defined PY_VER (
    echo   Python 3.11 NOT FOUND in WSL.
    echo   Install one of:
    echo     pyenv install 3.11.9 ^&^& pyenv global 3.11.9
    echo     sudo apt install python3.11 python3.11-venv
    exit /b 1
)
echo   Found: Python %PY_VER%

REM Verify buildozer + cython are installed
for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "python3.11 -m buildozer --version 2>/dev/null | head -1"`) do (
    set "BZ_VER=%%P"
)
if not defined BZ_VER (
    echo   buildozer NOT installed for python3.11.
    echo   Run inside WSL:
    echo     python3.11 -m pip install --user buildozer cython
    exit /b 1
)
echo   Found: buildozer %BZ_VER%

REM ---------------------------------------------------------------------------
REM  1. Locate Android SDK
REM ---------------------------------------------------------------------------
echo [1/6] Searching for Android SDK...
set "SDK_WSL="

for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -d $HOME/.pyside6_android_deploy/android-sdk && echo -n $HOME/.pyside6_android_deploy/android-sdk"`) do (
    if not "%%P"=="" set "SDK_WSL=%%P"
)

if not defined SDK_WSL (
    for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -n \"$ANDROID_HOME\" && test -d \"$ANDROID_HOME\" && echo -n $ANDROID_HOME"`) do (
        if not "%%P"=="" set "SDK_WSL=%%P"
    )
)
if not defined SDK_WSL (
    for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -n \"$ANDROIDSDK\" && test -d \"$ANDROIDSDK\" && echo -n $ANDROIDSDK"`) do (
        if not "%%P"=="" set "SDK_WSL=%%P"
    )
)
if not defined SDK_WSL (
    if exist "%LOCALAPPDATA%\Android\Sdk" (
        set "SDK_WIN=%LOCALAPPDATA%\Android\Sdk"
        set "TMP_SDK=!SDK_WIN:\=/!"
        set "SDK_WSL=/mnt/c!TMP_SDK:~2!"
    )
)

if not defined SDK_WSL (
    echo   NOT FOUND
    echo   Looked in:
    echo     - ~/.pyside6_android_deploy/android-sdk (WSL)
    echo     - $ANDROID_HOME / $ANDROIDSDK (WSL env)
    echo     - %LOCALAPPDATA%\Android\Sdk (Windows)
    echo   Install the Android SDK or set ANDROID_HOME in WSL.
    exit /b 1
)
echo   Found: %SDK_WSL%

REM ---------------------------------------------------------------------------
REM  2. Locate Android NDK
REM ---------------------------------------------------------------------------
echo [2/6] Searching for Android NDK...
set "NDK_WSL="

for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -d $HOME/.pyside6_android_deploy/android-ndk/android-ndk-r28c && echo -n $HOME/.pyside6_android_deploy/android-ndk/android-ndk-r28c"`) do (
    if not "%%P"=="" set "NDK_WSL=%%P"
)
if not defined NDK_WSL (
    for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -n \"$ANDROIDNDK\" && test -d \"$ANDROIDNDK\" && echo -n $ANDROIDNDK"`) do (
        if not "%%P"=="" set "NDK_WSL=%%P"
    )
)
if not defined NDK_WSL (
    for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "ls -d $HOME/.pyside6_android_deploy/android-ndk/* 2>/dev/null | head -1"`) do (
        if not "%%P"=="" set "NDK_WSL=%%P"
    )
)

if not defined NDK_WSL (
    echo   NOT FOUND
    echo   Looked in:
    echo     - ~/.pyside6_android_deploy/android-ndk/android-ndk-r28c (WSL)
    echo     - $ANDROIDNDK (WSL env)
    echo     - any dir under ~/.pyside6_android_deploy/android-ndk/
    exit /b 1
)
echo   Found: %NDK_WSL%

REM ---------------------------------------------------------------------------
REM  3. Locate or download wheels
REM ---------------------------------------------------------------------------
echo [3/6] Locating PySide6/Shiboken6 wheels...

if not exist "%WHEELS_WIN%" mkdir "%WHEELS_WIN%"

REM --- PySide6 ---
set "PYSIDE_LOCAL="
if exist "%WHEELS_WIN%\%PYSIDE_FILE_LOWER%" set "PYSIDE_LOCAL=%WHEELS_WIN%\%PYSIDE_FILE_LOWER%"
if not defined PYSIDE_LOCAL if exist "%WHEELS_WIN%\%PYSIDE_FILE_UPPER%" set "PYSIDE_LOCAL=%WHEELS_WIN%\%PYSIDE_FILE_UPPER%"
if not defined PYSIDE_LOCAL (
    for %%F in ("%WHEELS_WIN%\pyside6-*.whl") do (
        if exist "%%F" set "PYSIDE_LOCAL=%%F"
    )
)

if defined PYSIDE_LOCAL (
    echo   PySide6:   found %PYSIDE_LOCAL%
) else (
    echo   PySide6:   NOT FOUND - downloading...
    echo   URL: %PYSIDE_URL%
    powershell.exe -NoProfile -Command ^
      "try { Invoke-WebRequest -Uri '%PYSIDE_URL%' -OutFile '%WHEELS_WIN%\%PYSIDE_FILE_LOWER%' -UseBasicParsing } catch { Write-Error $_; exit 1 }"
    if errorlevel 1 (
        echo   Download FAILED.
        echo   Download manually: %PYSIDE_URL%
        echo   Place in: %WHEELS_WIN%
        exit /b 1
    )
    set "PYSIDE_LOCAL=%WHEELS_WIN%\%PYSIDE_FILE_LOWER%"
    echo   PySide6:   downloaded
)

REM --- Shiboken6 ---
set "SHIB_LOCAL="
if exist "%WHEELS_WIN%\%SHIB_FILE%" set "SHIB_LOCAL=%WHEELS_WIN%\%SHIB_FILE%"
if not defined SHIB_LOCAL (
    for %%F in ("%WHEELS_WIN%\shiboken6-*.whl") do (
        if exist "%%F" set "SHIB_LOCAL=%%F"
    )
)

if defined SHIB_LOCAL (
    echo   Shiboken6: found %SHIB_LOCAL%
) else (
    echo   Shiboken6: NOT FOUND - downloading...
    echo   URL: %SHIB_URL%
    powershell.exe -NoProfile -Command ^
      "try { Invoke-WebRequest -Uri '%SHIB_URL%' -OutFile '%WHEELS_WIN%\%SHIB_FILE%' -UseBasicParsing } catch { Write-Error $_; exit 1 }"
    if errorlevel 1 (
        echo   Download FAILED.
        echo   Download manually: %SHIB_URL%
        echo   Place in: %WHEELS_WIN%
        exit /b 1
    )
    set "SHIB_LOCAL=%WHEELS_WIN%\%SHIB_FILE%"
    echo   Shiboken6: downloaded
)

REM Ensure the lowercase PySide6 name exists too (some p4a tooling expects it)
if not exist "%WHEELS_WIN%\%PYSIDE_FILE_LOWER%" (
    if defined PYSIDE_LOCAL (
        copy /y "%PYSIDE_LOCAL%" "%WHEELS_WIN%\%PYSIDE_FILE_LOWER%" >nul 2>&1
    )
)

REM ---------------------------------------------------------------------------
REM  4. Locate or extract Qt Android jars
REM ---------------------------------------------------------------------------
echo [4/6] Locating Qt Android jars...
set "JARS_RESOLVED_WSL="

REM Prefer packaging/android/jars/
for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -f '%JARS_WSL%/Qt6Android.jar' && test -f '%JARS_WSL%/Qt6AndroidBindings.jar' && echo -n yes"`) do (
    if "%%P"=="yes" set "JARS_RESOLVED_WSL=%JARS_WSL%"
)

REM Fall back to deployment/jar/PySide6/jar/
if not defined JARS_RESOLVED_WSL (
    for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -f '%PROJECT_WSL%/deployment/jar/PySide6/jar/Qt6Android.jar' && test -f '%PROJECT_WSL%/deployment/jar/PySide6/jar/Qt6AndroidBindings.jar' && echo -n yes"`) do (
        if "%%P"=="yes" set "JARS_RESOLVED_WSL=%PROJECT_WSL%/deployment/jar/PySide6/jar"
    )
)

REM Extract from wheels
if not defined JARS_RESOLVED_WSL (
    echo   Extracting jars from PySide6 wheel...
    wsl.exe bash -lc "mkdir -p '%JARS_WSL%' && cd '%WHEELS_WSL%' && for w in *.whl; do [ -f \"$w\" ] && unzip -o -j \"$w\" 'PySide6/jar/*' -d '%JARS_WSL%' >/dev/null 2>&1 || true; done"
    for /f "usebackq delims=" %%P in (`wsl.exe bash -lc "test -f '%JARS_WSL%/Qt6Android.jar' && echo -n yes"`) do (
        if "%%P"=="yes" set "JARS_RESOLVED_WSL=%JARS_WSL%"
    )
)

if not defined JARS_RESOLVED_WSL (
    echo   NOT FOUND and extraction from wheels failed.
    echo   Verify %WHEELS_WIN% contains the PySide6 wheel.
    exit /b 1
)
echo   Found: %JARS_RESOLVED_WSL%

REM ---------------------------------------------------------------------------
REM  5. Rewrite buildozer.spec
REM ---------------------------------------------------------------------------
echo [5/6] Rewriting buildozer.spec...

copy /y "%SPEC_WIN%" "%SPEC_WIN%.bak" >nul

powershell.exe -NoProfile -Command ^
  "$spec = '%SPEC_WIN%';" ^
  "$root = '%PROJECT_WSL%';" ^
  "$sdk  = '%SDK_WSL%';" ^
  "$ndk  = '%NDK_WSL%';" ^
  "$jars = '%JARS_RESOLVED_WSL%';" ^
  "$c = Get-Content -Raw $spec;" ^
  "$c = [regex]::Replace($c, '(?m)^source\.dir\s*=.*$',         'source.dir = ' + $root);" ^
  "$c = [regex]::Replace($c, '(?m)^android\.sdk_path\s*=.*$',  'android.sdk_path = ' + $sdk);" ^
  "$c = [regex]::Replace($c, '(?m)^android\.ndk_path\s*=.*$',  'android.ndk_path = ' + $ndk);" ^
  "$c = [regex]::Replace($c, '(?m)^p4a\.local_recipes\s*=.*$', 'p4a.local_recipes = ' + $root + '/deployment/recipes');" ^
  "if ($c -match '(?m)^android\.add_jars\s*=.*$') {" ^
  "  $c = [regex]::Replace($c, '(?m)^android\.add_jars\s*=.*$', 'android.add_jars = ' + $jars + '/Qt6Android.jar,' + $jars + '/Qt6AndroidBindings.jar')" ^
  "} else {" ^
  "  $c = [regex]::Replace($c, '(?m)^android\.apptheme\s*=.*$', '$0' + [Environment]::NewLine + 'android.add_jars = ' + $jars + '/Qt6Android.jar,' + $jars + '/Qt6AndroidBindings.jar')" ^
  "}" ^
  "$hookLine = 'p4a.hook = ' + $root + '/deployment/recipes/p4a_hook.py';" ^
  "if ($c -match '(?m)^p4a\.hook\s*=.*$') {" ^
  "  $c = [regex]::Replace($c, '(?m)^p4a\.hook\s*=.*$', $hookLine)" ^
  "} else {" ^
  "  $c = [regex]::Replace($c, '(?m)^p4a\.setup_py\s*=.*$', '$0' + [Environment]::NewLine + $hookLine)" ^
  "}" ^
  "$icon = $root + '/packaging/android/icon.png';" ^
  "$c = [regex]::Replace($c, '(?m)^android\.icon\s*=.*$', 'android.icon = ' + $icon);" ^
  "$c = [regex]::Replace($c, '--icon=\S+', '--icon=' + $icon);" ^
  "Set-Content -NoNewline $spec $c"

if errorlevel 1 (
    echo   FAILED to rewrite spec.
    exit /b 1
)

REM ---------------------------------------------------------------------------
REM  6. Verify
REM ---------------------------------------------------------------------------
echo [6/6] Verifying spec...
echo.
findstr /B /C:"source.dir" /C:"android.sdk_path" /C:"android.ndk_path" /C:"android.add_jars" /C:"android.icon" /C:"p4a.local_recipes" /C:"p4a.branch" /C:"p4a.hook" /C:"p4a.extra_args" /C:"android.apptheme" "%SPEC_WIN%"

echo.
echo === Done ===
echo Spec:    %SPEC_WIN%
echo Backup:  %SPEC_WIN%.bak
echo.
echo Next: run installer\android\build_apk.bat
exit /b 0
