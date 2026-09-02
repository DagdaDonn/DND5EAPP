"""
Opt-in runtime diagnostics for tracking down UI bugs that only show up in
a real packaged build (flashing windows, toast timing, etc.) -- not needed
for normal operation, and OFF by default. Flip ENABLED to True (or just
the specific flag(s) below it) to reactivate a given trace without having
to re-thread logging calls through the call sites again.

Output goes through shared.py's write_diagnostic_log(), i.e. next to the
running executable when frozen (see diagnostic_log_dir()), same as
mimic_crash_log.txt -- that one is NOT part of this module and stays
always-on; it's the real crash safety net, not a debugging trace.

Author: Ethan O'Brien
Date: 2026-09-02
"""

ENABLED = False           # master switch -- flip True to re-enable everything below
LOG_TOASTS = ENABLED      # every _toast() call: message + call stack -> mimic_toast_log.txt
LOG_WINDOW_SHOWS = ENABLED  # every top-level QEvent.Show, app-wide -> mimic_window_log.txt


def log_toast(text: str) -> None:
    """Trace every toast fire (message + call stack). Was used to root-cause
    a report of a small popup flashing on character load/create -- that
    turned out to be a different bug (see log_window_show), so this can
    stay off, but the trace is cheap and easy to flip back on if another
    "why did a toast fire here" question comes up."""
    if not LOG_TOASTS:
        return
    try:
        import traceback
        from datetime import datetime as _dt
        from dnd_app.ui.shared import write_diagnostic_log
        entry = f"\n[{_dt.now().isoformat()}] toast: {text!r}\n" + "".join(traceback.format_stack()[:-1])
        write_diagnostic_log("mimic_toast_log.txt", entry, mode="a")
    except Exception:
        pass


def log_window_show(obj, event) -> None:
    """Trace every top-level window becoming visible, app-wide -- call from
    CharacterCreatorApp.eventFilter() on QEvent.Show. This is how the
    "flashing min/max/close popup on character load" bug was actually
    root-caused: a real live-run log showed a bare QLabel (abilities.py's
    save-advantage badge) becoming its own top-level window because
    setVisible(True) was called on it before it was ever added to a
    layout -- a QWidget with no parent yet is a genuine top-level window
    as far as Qt/the OS window manager is concerned. Fixed at the source
    (abilities.py); this trace is kept here, off by default, in case a
    similar "stray top-level window" report shows up again for a
    different widget."""
    if not LOG_WINDOW_SHOWS:
        return
    try:
        if not (hasattr(obj, "isWindow") and obj.isWindow()):
            return
        from dnd_app.ui.shared import write_diagnostic_log
        from datetime import datetime as _dt
        title = obj.windowTitle() if hasattr(obj, "windowTitle") else "?"
        entry = (f"\n[{_dt.now().isoformat()}] top-level window shown: "
                  f"class={type(obj).__name__!r} title={title!r} "
                  f"flags={int(obj.windowFlags())!r}\n")
        # A plain QLabel/QWidget/QFrame has no legitimate reason to ever be
        # its own top-level window (unlike QMenu, QFileDialog, QMessageBox,
        # etc., which are supposed to be) -- capture the live Python call
        # stack for just these so a report pins down the construction site
        # directly instead of another round of guessing.
        if type(obj).__name__ in ("QLabel", "QWidget", "QFrame"):
            import traceback
            entry += "".join(traceback.format_stack()[:-1])
        write_diagnostic_log("mimic_window_log.txt", entry, mode="a")
    except Exception:
        pass
