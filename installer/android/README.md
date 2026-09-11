# installer/android

See [`../../packaging/android/BUILD_APK.md`](../../packaging/android/BUILD_APK.md)
for the build guide, and `packaging/android/README.md` for what the
build's config file (`pysidedeploy.spec`) needs to contain and why.
`build_apk.bat` (Windows) and `build_apk.sh` (Linux/macOS) both wrap
`pyside6-android-deploy`, the way `installer/windows/build_exe.bat`/
`.sh` wrap PyInstaller -- pick whichever matches your machine, they do
the same four steps.

Untested in this sandbox (no Android SDK/NDK available here) — see
`packaging/android/BUILD_APK.md`'s note at the top before relying on it.
