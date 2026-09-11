# packaging/android

Holds the Android build configuration for MIMIC, the way
`packaging/windows/DnD5eCharacterCreator.spec` holds it for the Windows
EXE. `dnd_app/ui_android/` has several real, working screens (Race,
Abilities, Class, Equipment, Character Sheet, Save/Load, Settings —
see `dnd_app/ui_android/README.md`), so this is no longer a "nothing to
build yet" placeholder.

**Just want to build the APK?** Start at
`BUILD_APK.md` instead — it's the plain-language,
numbered walkthrough (install a couple of programs, run one script,
copy the file to your phone). Everything below this point is reference
material for that guide's step 5 (generating/adjusting
`pysidedeploy.spec`) and for troubleshooting — not something you need
to read start to finish before your first build.

**Nothing in this folder has been build-tested.** This sandbox has no
Android SDK/NDK, so none of the commands below have actually been run
here — unlike the Windows `.spec`, which was verified against a real
build earlier in this project. Treat this as a starting guide, and
expect to adjust it against whatever `pyside6-android-deploy` version
you actually have installed.

## The tool

PySide6 (6.5+) ships `pyside6-android-deploy`, a wrapper around
[python-for-android](https://github.com/kivy/python-for-android) —
there's no PyInstaller-for-Android equivalent; Windows and Android use
genuinely different packaging tools, not just different config files
for the same one.

```bash
pip install PySide6          # pyside6-android-deploy lands on PATH with it
pyside6-android-deploy --help
```

## Prerequisites (all external to this repo)

| Requirement | Notes |
|---|---|
| JDK | 17 is the current Qt-recommended version — check `pyside6-android-deploy --help` / release notes for what your installed PySide6 version expects, this drifts between Qt releases |
| Android SDK | cmdline-tools, platform-tools, and a build-tools version matching your target SDK |
| Android NDK | a *specific* pinned version per Qt release, not "whatever's newest" — using the wrong NDK version is the most common cause of a broken build with this tooling |
| `ANDROID_SDK_ROOT`, `ANDROID_NDK_ROOT` | env vars the deploy tool reads to find the above |
| A PySide6 build for Android | the deploy tool needs Android-target PySide6/Shiboken wheels, not the desktop `pip install PySide6` — it downloads these itself, but they're large and version-locked to your Qt release |

## The config file: `pysidedeploy.spec`

This is the real per-app config the deploy tool reads (INI-format), the
Android equivalent of the `.spec` file on the Windows side — but its
exact field set has changed across Qt releases, and hand-writing one
from memory risks silently drifting from whatever your installed
version actually parses. The correct way to get one that's guaranteed
to match your toolchain:

```bash
cd /path/to/DND5EAPP
pyside6-android-deploy --init --input-file dnd_app/ui_android/main.py
```

This generates `pysidedeploy.spec` in the current directory, pre-filled
for the project it's pointed at. Move it into `packaging/android/` once
generated, then adjust the fields below to match MIMIC specifically:

- **Entry point** — `dnd_app/ui_android/main.py`, not the desktop
  `run_dnd_creator.py`. The generator's `--input-file` flag above
  already points at the right one.
- **App data** — `dnd_app/data/` and `dnd_app/core/` need to be
  bundled as part of the app's Python source, the same requirement the
  Windows spec handles via PyInstaller's `datas=[...]` (see that file's
  comments). Whatever the generated spec calls its "extra files/dirs to
  include" field, point it at those two directories plus
  `dnd_app/ui_android/qml/` (the QML files and the `Mimic` import
  module aren't `.py` files, so they need to be listed explicitly the
  same way `dnd_app/ui_desktop/icon.ico` is in the Windows spec — a
  static-analysis import tracer has nothing to trace them from).
- **Qt modules** — this app uses `QtCore`, `QtGui`, `QtQml`, `QtQuick`,
  `QtQuickControls2` (Basic + Material styles). Whatever's excluded by
  default should be checked against this list — the Windows spec's
  aggressive module-exclusion approach doesn't transfer directly since
  Quick/QML/QuickControls2 are used here, unlike the QtWidgets-only
  desktop app that excludes exactly those.
- **Package name** — pick a real reverse-DNS package id
  (`com.<you>.mimic` or similar) before ever doing a release build;
  changing it later means Android treats it as a different app
  entirely (no seamless update path for existing installs).
- **Permissions** — see below.
- **Architecture** — `arm64-v8a` alone covers the large majority of
  real devices. Add `armeabi-v7a` only if you need to support very old
  hardware, and `x86_64` only for emulator testing — each additional
  ABI roughly multiplies the bundled Qt/Python payload size.
- **min/target SDK** — target whatever's current for Play Store
  submission at build time; that requirement moves roughly yearly.

## Permissions this app will need

The desktop app's save/load/export (`dnd_app/core/save_load.py`,
`dnd_app/core/pdf_export.py`) currently assumes free filesystem access
to wherever the user points a file dialog. Android doesn't work that
way past API 29 (scoped storage) — a real Android release needs one of:

- The Storage Access Framework (`ACTION_OPEN_DOCUMENT`/
  `ACTION_CREATE_DOCUMENT` intents) instead of a raw file-path dialog,
  or
- App-private storage (`Context.getFilesDir()`-equivalent) with no
  extra permission needed, if characters don't need to be visible to
  other apps / survive an uninstall.

This is a real design decision for whoever wires up
`dnd_app/ui_android`'s save/load screens, not just a build-config
checkbox — flagging it here since it'll block a release build's
Play Store review (`MANAGE_EXTERNAL_STORAGE` is heavily restricted and
usually the wrong answer) even after the packaging itself works.

## Icon

Android wants a full adaptive-icon set (`mipmap-mdpi` through
`mipmap-xxxhdpi`, plus a foreground/background layer pair for the
adaptive format), not the single `.ico` the Windows build uses. The
deploy tool can generate the density set from one source PNG — check
`pyside6-android-deploy --help` for the current flag name — but the
adaptive foreground/background split needs to be prepared by hand from
whatever replaces `dnd_app/ui_desktop/icon.ico` for this platform.

## Building

Once `pysidedeploy.spec` exists in this folder and the prerequisites
above are installed:

```bash
pyside6-android-deploy --config-file packaging/android/pysidedeploy.spec
```

produces an (unsigned, for a debug build) `.apk`. See
`BUILD_APK.md` for the wrapper script and release
signing.
