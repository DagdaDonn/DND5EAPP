# Building MIMIC for Android

This turns the app into an `.apk` file you can copy to your phone and
install, the same way `installer\windows\build_exe.bat` turns it into
`MIMIC.exe`. Android just needs more one-time setup first, because
Google's own Android build tools (not this project) require it —
nothing here is MIMIC-specific complexity.

**Untested in this sandbox** — there's no Android SDK/NDK here to run
against. Everything below should work, but if a step doesn't match
what you see on your machine, that's the kind of thing to fix as you
go rather than a sign you did something wrong.

## First-time setup (do this once)

1. **Install a JDK (Java).** Get [Eclipse Temurin 17](https://adoptium.net/) —
   pick the installer for your OS, run it, done.
2. **Install Android Studio.** Get it from
   [developer.android.com/studio](https://developer.android.com/studio).
   You will NOT write any Android code — you're only using its
   installer to get the Android SDK and NDK, which is far easier than
   installing those two by hand.
3. **Open Android Studio once, then install the NDK through it:**
   - `More Actions` (or `Tools`) → `SDK Manager`
   - `SDK Tools` tab → tick **NDK (Side by side)** → `Apply`
   - Note the folder path shown at the top of that window (the
     "Android SDK Location") — you need it in the next step.
4. **Tell your computer where those live.** Two settings, set once:
   - `ANDROID_SDK_ROOT` = the SDK Location path from step 3
     (something like `C:\Users\<you>\AppData\Local\Android\Sdk`)
   - `ANDROID_NDK_ROOT` = the same path, plus `\ndk\<version folder>`
     (the SDK Manager's NDK entry shows the exact version number)

   **Windows:** Start menu → search "environment variables" → "Edit
   the system environment variables" → `Environment Variables...` →
   `New...` under "User variables" for each of the two above. (Or, in
   a Command Prompt: `setx ANDROID_SDK_ROOT "C:\path\to\Sdk"` — close
   and reopen the terminal afterward for it to take effect.)

   **macOS/Linux:** add two lines like
   `export ANDROID_SDK_ROOT=$HOME/Android/Sdk` to your shell's profile
   file (`~/.zshrc`, `~/.bashrc`, etc.), then restart the terminal.
5. **Generate the one config file the build needs**, from the repo root:
   ```
   pip install PySide6
   pyside6-android-deploy --init --input-file dnd_app/ui_android/main.py
   ```
   This creates `pysidedeploy.spec` in the folder you ran it from —
   move it into `packaging/android/`. See `packaging/android/README.md`
   for the handful of fields worth checking/adjusting in it (what to
   bundle, the app's package name, etc.) — skippable on a first try,
   the generated defaults are usually enough to get a working APK.

That's the whole one-time setup. You won't need to repeat any of it
for future builds — steps 1-4 install real programs on your computer,
and step 5's file stays in the repo once created.

## Every time you want a new build

**Windows:** double-click `installer\android\build_apk.bat` (or run it
from a Command Prompt).

**macOS/Linux:** run `installer/android/build_apk.sh` from the repo
root (or from inside `installer/android/`).

Either script checks your setup, installs/updates PySide6, and runs
the actual Android build tool. **The first build is slow** — 15-40
minutes isn't unusual, since it's compiling a full Python-for-Android
distribution, not just packaging already-installed files the way the
Windows build does. Later builds are faster.

When it finishes, it prints where the `.apk` file landed. **Copy that
file to your phone** (USB cable, email it to yourself, a cloud drive —
any way you'd normally move a file over) and tap it there to install.
Your phone will warn about installing from an unknown source the first
time — that's normal for any app not from the Play Store; allow it for
this one file.

---

## Good to know

- This produces a **debug-signed** APK. That's completely fine for
  installing on your own phone. It only matters if you ever want to
  publish MIMIC on the Play Store — see "Signing" below for that case.
- `pyside6-android-deploy` runs natively on Windows (since PySide6
  6.5) — you do not need WSL or a separate Linux machine.

## Signing (only needed for a Play Store release, not for your own phone)

1. Create a keystore: `keytool -genkey -v -keystore mimic-release.keystore ...`
   — **do not commit this file to the repo**; treat it like a password.
   Losing it means losing the ability to publish updates to an
   already-published app listing.
2. Sign the build's output with `apksigner`, or set the keystore
   path/alias directly in `pysidedeploy.spec` if your installed
   version supports that (`pyside6-android-deploy --help`).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| "ANDROID_SDK_ROOT is not set" / "...NDK_ROOT is not set" | Step 4 above didn't take effect — close and reopen your terminal (or restart your computer) after setting it |
| "pysidedeploy.spec not found" | Step 5 above wasn't done yet, or the generated file wasn't moved into `packaging/android/` |
| Build fails deep inside `python-for-android` mentioning a missing NDK component | NDK version mismatch — this tooling wants the exact NDK version your Qt release expects, not "whatever's newest"; check `packaging/android/README.md` |
| `ModuleNotFoundError` for `dnd_app.core`/`dnd_app.data` at runtime on-device | Those folders aren't listed in the spec's "extra files to include" field — see `packaging/android/README.md`'s "App data" note |
| QML files load a blank screen on-device but work in desktop testing | The QML/`Mimic` import files weren't bundled — same cause as above |
| Save/Export crashes or silently does nothing on-device | Expected until the storage-permissions item in `packaging/android/README.md` is resolved |
