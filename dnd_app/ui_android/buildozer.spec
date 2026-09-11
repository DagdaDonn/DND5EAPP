[app]

title = MIMIC
package.name = mimic
package.domain = org.mimic

source.dir = /mnt/c/Users/OBRIET/Dev/Projects/Extra/DND/DND5EAPP
source.include_exts = py,qml,png,jpg,jpeg,ico,gif,svg,pdf,json,md,ttf
source.include_patterns = packaging/android/icon.png
source.exclude_dirs = .git,build,dist,deployment,.buildozer,packaging/windows,installer,mimic_app_reference
source.exclude_patterns = *.whl,*.pyc,*.pyo,buildozer.spec,buildozer.spec.*,pysidedeploy.spec

version = 0.1
requirements = python3,shiboken6,PySide6

orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 21
android.ndk_api = 21
android.sdk_path = /home/eobrien/.pyside6_android_deploy/android-sdk
android.ndk_path = /home/eobrien/.pyside6_android_deploy/android-ndk/android-ndk-r28c
android.archs = arm64-v8a
android.allow_backup = True

android.permissions = android.permission.INTERNET,android.permission.ACCESS_NETWORK_STATE,android.permission.WRITE_EXTERNAL_STORAGE

android.apptheme = "@android:style/Theme.NoTitleBar"

# PySide6-specific: this is the Qt bootstrap, not SDL2
p4a.bootstrap = qt
p4a.branch = v2024.01.21

# Local recipes provide the Qt bootstrap glue
p4a.local_recipes = /mnt/c/Users/OBRIET/Dev/Projects/Extra/DND/DND5EAPP/deployment/recipes

# Which Qt modules the app uses
android.qt_libs = Quick,Core,Qml,Gui,QuickControls2,OpenGL,Network

# Don't run setup.py
p4a.setup_py = false

# Hook to load the Qt Android platform plugin
p4a.hook = 

# Extra args to p4a — matches what pysidedeploy.spec passes
p4a.extra_args = --load-local-libs=plugins_platforms_qtforandroid --qt-libs=Quick,Core,Qml,Gui,QuickControls2,OpenGL,Network

[buildozer]
log_level = 2
warn_on_root = 0
