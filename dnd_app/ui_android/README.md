# ui_android (v3 scaffold — not yet implemented)

This package is reserved for MIMIC's touch-first Android UI. Nothing
here runs yet; this file exists so the folder split doesn't look like
an accident once real work starts.

## Plan

- **Framework:** Qt Quick/QML rather than QtWidgets. `ui_desktop/` is
  QtWidgets, which is a poor fit for touch (no gestures, tiny desktop-
  scaled click targets, hover-only tooltips as the sole way to see a
  lot of information) and PyInstaller/Windows-oriented packaging.
  Qt's own Android deployment tooling is built around Qt Quick, not
  QtWidgets, so this is the path of least resistance for actually
  shipping an APK from PySide6.
- **Not a port.** The desktop UI's screen layouts (side-by-side
  multi-column tabs, dense stat bars, double-click-to-rename, hover-
  dependent affordances) don't translate to a phone screen and won't
  be carried over as-is. Each screen gets redesigned for touch and
  small-screen real estate, starting from what the player actually
  needs visible at once on a phone.
- **Shared with desktop:** `dnd_app/core/` and `dnd_app/data/` — the
  character model, calculator, builder, save/load, and all game-rules
  data. Zero Qt dependency in either, so nothing there needs to change
  for this to work; both UIs read and write the same character dict
  shape and the same save-file format.
- **Not shared:** everything in `dnd_app/ui_desktop/`. No QtWidgets
  code is reused directly; QML screens are new files here.

## Status

Empty scaffold only. See `packaging/android/` and `installer/android/`
for the matching build-tooling placeholders.
