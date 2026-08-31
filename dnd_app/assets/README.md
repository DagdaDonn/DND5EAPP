Drop `splash.gif` (preferred, animated) or `splash.png` (static) in this
folder to replace the default startup splash screen. No code changes needed
— `dnd_app/ui/splash.py` picks either file up automatically if present.

`5E_CharacterSheet_Fillable.pdf` is WotC's official free 3-page fillable
2014 PHB character sheet (distributed for personal use — see the notice
printed at the bottom of each page). `dnd_app/core/pdf_export.py` fills it
with a character's real data for the "Export Character" → "Official
character sheet (PDF)" option. Its field-ID mapping is hardcoded against
this exact file's own form fields — if this PDF is ever replaced with a
different version, that mapping needs to be re-derived (see the module's
own docstring for how it was built the first time).
