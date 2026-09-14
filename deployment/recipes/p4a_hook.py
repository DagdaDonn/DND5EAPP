"""
python-for-android hook:
1. before_apk_build:
   - ensure libc++_shared.so is present in the dist libs dirs
   - copy Qt native .so files from the PySide6 bundle into libs/arm64-v8a/
     so Android's System.loadLibrary("Qt6Quick") etc. can find them
2. before_apk_assemble: patch PythonActivity.java for Qt 6.11 compat
"""
import os
import shutil
from pathlib import Path
from pythonforandroid.logger import info, warning


HELPER_METHOD = '''    public void setEnvironmentVariable(String key, String value) {
        /** Sets an environment variable using the OS-level API. */
        try {
            android.system.Os.setenv(key, value, true);
            android.util.Log.v("PythonActivity", "setenv " + key + "=" + value);
        } catch (Exception e) {
            android.util.Log.e("Qt bootstrap", "Unable set environment variable:" + key + "=" + value);
            e.printStackTrace();
        }
    }

'''


CALL_START_APPLICATION = '''        android.util.Log.v("PythonActivity", "->> Returned from super.onCreate(), invoking QtNative.startApplication");
        try {
            java.lang.reflect.Method m = Class.forName("org.qtproject.qt.android.QtNative")
                .getDeclaredMethod("startApplication", String.class, String.class);
            m.setAccessible(true);
            m.invoke(null, "org.kivy.android.PythonActivity", "");
        } catch (Throwable t) {
            android.util.Log.e("PythonActivity", "Failed to call QtNative.startApplication: " + t);
            t.printStackTrace();
        }
        android.util.Log.v("PythonActivity", "->> QtNative.startApplication returned");'''


def _patch_java_file(path):
    p = Path(path)
    if not p.exists():
        return False
    src = p.read_text()
    orig = src
    src = src.replace("QtNative.setEnvironmentVariable(", "setEnvironmentVariable(")
    src = src.replace("import org.qtproject.qt.android.QtNative;\n", "")
    marker = "    @Override\n"
    if (marker in src
            and "public void setEnvironmentVariable(String key, String value)" not in src):
        src = src.replace(marker, HELPER_METHOD + marker, 1)
    if "Class.forName(\"org.qtproject.qt.android.QtNative\")" not in src:
        log_marker = "        super.onCreate(savedInstanceState);"
        insertion = log_marker + "\n" + CALL_START_APPLICATION
        if log_marker in src:
            src = src.replace(log_marker, insertion, 1)
    if src != orig:
        p.write_text(src)
        return True
    return False


def _dist_dir(toolchain):
    try:
        dist = getattr(toolchain, "_dist", None)
        if dist is not None:
            return Path(getattr(dist, "dist_dir"))
    except Exception:
        pass
    return Path.cwd()


def _copy_qshared_libs(dist):
    """Copy libQt6*.so and other runtime libs from the PySide6 bundle into libs/arm64-v8a/."""
    dest = dist / "libs" / "arm64-v8a"
    dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    sources = []

    # The PySide6 Qt lib directory inside the unpacked bundle
    for pattern in ("_python_bundle__arm64-v8a/_python_bundle/site-packages/PySide6/Qt/lib",
                    "_python_bundle/site-packages/PySide6/Qt/lib"):
        candidate = dist / pattern
        if candidate.exists():
            sources.append(candidate)

    for src_dir in sources:
        info(f"p4a_hook: scanning {src_dir}")
        for so in src_dir.glob("*.so"):
            # Skip symlinks and directories
            if not so.is_file():
                continue
            target = dest / so.name
            # Don't overwrite a newer copy that p4a may already have placed
            if target.exists() and target.stat().st_mtime >= so.stat().st_mtime:
                continue
            try:
                shutil.copy2(so, target)
                copied += 1
            except Exception as e:
                warning(f"p4a_hook: failed to copy {so} -> {target}: {e}")

    info(f"p4a_hook: copied {copied} Qt/FFmpeg .so files into {dest}")


def before_apk_build(toolchain, *args, **kwargs):
    info("p4a_hook: before_apk_build — ensuring libc++_shared.so and Qt libs are present")
    dist = _dist_dir(toolchain)
    info(f"p4a_hook: dist = {dist}")

    # 1. libc++_shared.so from the NDK
    ndk = os.environ.get("ANDROIDNDK")
    if ndk:
        candidates = list(Path(ndk).rglob("libc++_shared.so"))
        chosen = None
        for c in candidates:
            if "aarch64" in str(c):
                chosen = c
                break
        if chosen is None and candidates:
            chosen = candidates[0]
        if chosen is not None:
            dest_dir = dist / "libs" / "arm64-v8a"
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(chosen, dest_dir / "libc++_shared.so")
            info(f"p4a_hook: copied libc++_shared.so from {chosen}")
            stale = dist / "src" / "main" / "jniLibs" / "arm64-v8a" / "libc++_shared.so"
            if stale.exists():
                stale.unlink()
    else:
        warning("p4a_hook: ANDROIDNDK not set; cannot locate libc++_shared.so")

    # 2. Qt runtime libraries from the PySide6 bundle
    _copy_qshared_libs(dist)


def before_apk_assemble(toolchain, *args, **kwargs):
    info("p4a_hook: before_apk_assemble — patching PythonActivity.java")
    dist = _dist_dir(toolchain)
    target = dist / "src/main/java/org/kivy/android/PythonActivity.java"
    if not target.exists():
        warning(f"p4a_hook: PythonActivity.java not found at {target}")
        return
    if _patch_java_file(target):
        info(f"p4a_hook: PATCHED {target}")
    else:
        info(f"p4a_hook: no change needed {target}")
