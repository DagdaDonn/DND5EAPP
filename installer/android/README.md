# installer/android

`build_apk.bat` (Windows) and `build_apk.sh` (Linux/macOS) run the
actual Android build — same split as `installer/windows/build_exe.bat`/
`.sh` wrapping PyInstaller for the desktop EXE. `packaging/android/`
holds the build-target manifest and setup (`pysidedeploy.spec`,
`setup_buildozer_spec.bat`) — see
[`../../packaging/android/BUILD_APK.md`](../../packaging/android/BUILD_APK.md)
for the full build guide.

First time only, run `packaging\android\setup_buildozer_spec.bat`
before `build_apk.bat` to populate `buildozer.spec`'s SDK/NDK/wheel/jar
paths.

Untested in this sandbox (no Android SDK/NDK available here) — see
`packaging/android/BUILD_APK.md`'s note at the top before relying on it.
