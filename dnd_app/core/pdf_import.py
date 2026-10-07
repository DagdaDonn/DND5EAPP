"""
Import a character from a filled-in official WotC 5E character sheet PDF
(the 3-page "5E_CharacterSheet_Fillable.pdf" -- the same template
pdf_export.py fills, so its field IDs are known).

Two ways a typed sheet can arrive:
  * still fillable (typed in Acrobat, a phone PDF app, or exported by
    this app or another tool that fills the same form) -- the form fields
    hold the values, read directly;
  * flattened ("printed to PDF", or a viewer that bakes the form in) --
    no form fields left, so the text drawn on each page is matched to the
    template's own field boxes by position. Checkboxes can't be read this
    way (they're only drawn shapes), so proficiencies are worked out from
    the skill/save bonuses instead.

A scanned or photographed sheet has no text at all -- that would need OCR
and isn't handled here.

The sheet only holds what's written on it, so the character is rebuilt the
same way a new one is (race/class/background grants), and the sheet's own
numbers are then laid over the top: ability scores (racial bonuses
subtracted back out), proficiencies and expertise, max HP, spells, gear.
Anything that couldn't be matched to the app's data is kept, word for
word, in a "Imported from PDF" notes page so nothing typed is lost.
"""
from __future__ import annotations

import re

from .pdf_export import (
    TEMPLATE_PATH, SAVE_CHECKBOXES, SKILL_CHECKBOXES, SKILL_TEXT_FIELDS, SAVE_TEXT_FIELDS,
    ABILITY_SCORE_FIELDS, ABILITY_MOD_FIELDS, DEATH_SAVE_SUCCESS_CHECKBOXES, DEATH_SAVE_FAILURE_CHECKBOXES,
    WEAPON_FIELDS, SPELL_LEVEL_FIELDS, SLOT_FIELDS,
)

ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")

ALIGNMENTS = {
    "lg": "Lawful Good", "ng": "Neutral Good", "cg": "Chaotic Good",
    "ln": "Lawful Neutral", "n": "True Neutral", "tn": "True Neutral", "cn": "Chaotic Neutral",
    "le": "Lawful Evil", "ne": "Neutral Evil", "ce": "Chaotic Evil",
    "neutral": "True Neutral", "true neutral": "True Neutral",
}


# Shown before the player picks a file (both apps), so they know what to
# expect from a PDF import.
PDF_IMPORT_INTRO = ("A filled-in official 5e character sheet PDF (the 3-page Wizards of the "
                    "Coast sheet) becomes a character: ability scores, proficiencies, HP, "
                    "spells, gear, magic items, money and your notes.")
PDF_IMPORT_LIMITS = [
    "Only the official 5e sheet -- other layouts (D&D Beyond's PDF, homemade sheets) can't be read.",
    "It has to be typed: a scanned, photographed or handwritten sheet has no text to read.",
    "A \"printed to PDF\" (flattened) sheet loses its tick boxes, so proficiencies are worked "
    "out from the bonuses -- check prepared spells and death saves.",
    "The sheet only has room for so many spells per level; any that didn't fit aren't there to bring in.",
    "Anything it can't match is kept, word for word, on an \"Imported from PDF\" notes page, "
    "along with a list of things to check.",
]


class SheetImportError(ValueError):
    """The file isn't a readable official character sheet."""


# ── Reading the PDF ──────────────────────────────────────────────────────
_TEMPLATE_RECTS = None


def _template_rects() -> dict:
    """{field id: (page index, (x0, y0, x1, y1))} from the bundled template."""
    global _TEMPLATE_RECTS
    if _TEMPLATE_RECTS is None:
        from pypdf import PdfReader
        rects = {}
        for pi, page in enumerate(PdfReader(TEMPLATE_PATH).pages):
            for annot in page.get("/Annots") or []:
                a = annot.get_object()
                name = a.get("/T")
                if name is None and a.get("/Parent") is not None:
                    name = a["/Parent"].get_object().get("/T")
                if name is None or a.get("/Rect") is None:
                    continue
                x0, y0, x1, y1 = (float(v) for v in a["/Rect"])
                rects.setdefault(str(name), (pi, (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))))
        _TEMPLATE_RECTS = rects
    return _TEMPLATE_RECTS


def _is_checked(v) -> bool:
    return v not in (None, "", "/Off", "Off", "/No", "No", "0", "/0", False)


def _form_values(reader) -> dict:
    """Field id -> value (str, or bool for checkboxes) from a fillable PDF."""
    fields = reader.get_fields() or {}
    out = {}
    for name, f in fields.items():
        v = f.get("/V")
        if f.get("/FT") == "/Btn":
            out[name] = _is_checked(v)
        elif v is not None:
            out[name] = str(v)
    return out


def _flattened_values(reader) -> dict:
    """Text drawn inside each template field box, for a flattened sheet.

      for each of the 3 pages:
        collect every piece of text pypdf finds, with where it was drawn
        work out each piece's real position on the page (see the note on
          form XObjects below)
        drop each piece into the template field box it lands in
        join each box's pieces top-to-bottom into lines"""
    rects = _template_rects()
    by_page = {}
    for name, (pi, r) in rects.items():
        by_page.setdefault(pi, []).append((name, r))
    out = {}
    for pi, page in enumerate(reader.pages[:3]):
        boxes = by_page.get(pi, [])
        calls = []

        def visit(text, cm, tm, font, size, calls=calls):
            if text and text.strip():
                calls.append((text, list(cm), list(tm)))

        try:
            page.extract_text(visitor_text=visit)
        except Exception:
            continue
        # Text in a form XObject (how flattened fields are usually drawn) is
        # reported twice by pypdf: first piece by piece at its position
        # inside the field box (no page offset), then all together with the
        # box's placement as `cm` but a stale text matrix. So when a placed
        # report arrives, the run of local reports just before it that spells
        # the same text is moved by that cm, and the combined one dropped.
        squash = lambda t: re.sub(r"\s+", "", t)
        placed, local_run = [], []      # local_run: indexes into placed
        for text, cm, tm in calls:
            identity = cm[:4] == [1, 0, 0, 1] and cm[4] == 0 and cm[5] == 0
            if not identity:
                target, joined, k = squash(text), "", None
                for n in range(len(local_run), 0, -1):
                    joined = "".join(squash(placed[idx][0]) for idx in local_run[-n:])
                    if joined == target:
                        k = n
                        break
                if k:
                    for idx in local_run[-k:]:
                        t0, lx, ly = placed[idx]
                        placed[idx] = (t0, cm[4] + lx, cm[5] + ly)
                    local_run = []
                    continue
                local_run = []
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            placed.append((text, x, y))
            if identity:
                local_run.append(len(placed) - 1)
        pieces = {}
        for text, x, y in placed:
            for name, (x0, y0, x1, y1) in boxes:
                if x0 - 1 <= x <= x1 + 1 and y0 - 1 <= y <= y1 + 1:
                    pieces.setdefault(name, []).append((-y, x, text))
                    break
        for name, parts in pieces.items():
            parts.sort()
            lines, last_y = [], None
            for ny, _x, t in parts:
                if last_y is None or abs(ny - last_y) > 2:
                    lines.append(t)
                else:
                    lines[-1] += t
                last_y = ny
            out[name] = "\n".join(l.strip() for l in lines if l.strip())
    return out


def read_sheet_values(path_or_stream) -> tuple[dict, str]:
    """(values, how) where how is "form" or "flattened". Raises
    SheetImportError if it isn't the official sheet or has nothing typed.

      open the PDF (an unlocked one; a password stops here)
      if it has form fields:
        mostly the template's own field ids -> read them ("form"),
          unless every one is blank (an empty sheet)
        otherwise -> some other form, not the official sheet
      no form fields (flattened):
        no text at all -> a scan or photo, can't be read
        page 1 lacks the sheet's printed labels -> not the official sheet
        else -> read the text by position ("flattened")"""
    from pypdf import PdfReader
    try:
        reader = PdfReader(path_or_stream)
    except Exception as e:
        raise SheetImportError(f"Couldn't read the PDF ({e}).")
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise SheetImportError("The PDF is password protected.")
    known = set(_template_rects())
    values = _form_values(reader)
    if values and len(set(values) & known) >= 0.5 * len(known):
        if any(v for k, v in values.items() if isinstance(v, str) and v.strip()):
            return values, "form"
        raise SheetImportError("The character sheet is empty -- nothing has been typed into it.")
    if values:
        raise SheetImportError("This PDF has a form, but it isn't the official 5e character sheet.")
    flat = _flattened_values(reader)
    page1 = (reader.pages[0].extract_text() or "").upper() if reader.pages else ""
    if not flat or ("CLASS & LEVEL" not in page1 and "CHARACTER NAME" not in page1):
        if not page1.strip():
            raise SheetImportError("This PDF has no text in it (a scan or photo?) -- "
                                   "only typed, digital sheets can be imported.")
        raise SheetImportError("This doesn't look like the official 5e character sheet.")
    return flat, "flattened"


# ── Matching what's written to the app's data ────────────────────────────
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9+]+", " ", (s or "").lower()).strip()


def _int(s, default=None):
    m = re.search(r"[-+]?\d+", str(s or "").replace(",", ""))
    return int(m.group()) if m else default


def _best_match(text: str, names, min_len: int = 3):
    """The longest catalogue name found inside `text` (case/punctuation
    insensitive, whole words), else None."""
    t = f" {_norm(text)} "
    best = None
    for n in names:
        nn = _norm(n)
        if len(nn) >= min_len and f" {nn} " in t and (best is None or len(nn) > len(_norm(best))):
            best = n
    return best


def _exact(text: str, names):
    t = _norm(text)
    return next((n for n in names if _norm(n) == t), None)


def _race_and_subrace(text: str):
    from dnd_app.data.phb2014.races import RACE_DICT, RACE_NAMES
    if not text.strip():
        return "", ""
    race = _best_match(text, RACE_NAMES)
    if not race:
        return "", ""
    subrace = ""
    rest = f" {_norm(text)} "
    for sub_str in RACE_DICT.get(race, {}).get("subraces", []):
        sub = sub_str.split("(")[0].strip()
        if sub and f" {_norm(sub)} " in rest and len(sub) > len(subrace):
            subrace = sub
    return race, subrace


def _classes(text: str):
    """"Wizard 5 / Cleric 2", "Fighter 3, Rogue 2", "Lvl 4 Bard" ->
    [(class, level), ...]."""
    from dnd_app.data.phb2014.classes import CLASS_NAMES
    out = []
    names = sorted(CLASS_NAMES, key=len, reverse=True)
    t = text or ""
    for n in names:
        for m in re.finditer(re.escape(n), t, re.I):
            if any(m.start() < e and m.end() > s for _, _, s, e in out):
                continue
            after = re.match(r"\s*(?:\([^)]*\))?\s*(?:lvl\.?|level)?\s*(\d{1,2})", t[m.end():], re.I)
            before = re.search(r"(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:lvl\.?|level)?\s*$", t[:m.start()], re.I)
            lvl = int(after.group(1)) if after else (int(before.group(1)) if before else 1)
            out.append((n, max(1, min(20, lvl)), m.start(), m.end()))
    out.sort(key=lambda x: x[2])
    return [(n, l) for n, l, _, _ in out]


def _subclass_for(class_name: str, text: str) -> str:
    from dnd_app.data.phb2014.classes import CLASS_DICT
    from .character import clean_subclass_name
    best = ""
    for raw in CLASS_DICT.get(class_name, {}).get("subclasses", []):
        name = clean_subclass_name(raw)
        # "School of Evocation" is also written "Evocation"
        short = re.sub(r"^(school|college|circle|oath|path|way|domain|order|"
                       r"conclave|archetype|patron|tradition|the)\s+of\s+(the\s+)?", "", name, flags=re.I)
        for cand in {name, short}:
            if len(cand) > 3 and f" {_norm(cand)} " in f" {_norm(text)} " and len(name) > len(best):
                best = name
    return best


def _lines(text: str) -> list[str]:
    parts = []
    for line in (text or "").replace("\r", "\n").split("\n"):
        line = line.strip(" •-*\t")
        if not line:
            continue
        # a "(...)" wrapped onto its own line by a narrow box -- "Cloak of
        # Protection (equipped)" -- belongs to the line above
        if parts and line.startswith("(") and line.endswith(")") and not parts[-1].endswith((".", ":")):
            parts[-1] += " " + line
        else:
            parts.append(line)
    return parts


_QTY_PATTERNS = (
    re.compile(r"^(\d+)\s*[x×]\s*(.+)$", re.I),       # 2x Torch
    re.compile(r"^(.+?)\s*[x×]\s*(\d+)$", re.I),       # Torch x2
    re.compile(r"^(.+?)\s*\((\d+)\)$"),                # Torch (2)
    re.compile(r"^(\d+)\s+(.+)$"),                     # 10 Torches
)


def _split_qty(line: str):
    for i, pat in enumerate(_QTY_PATTERNS):
        m = pat.match(line)
        if m:
            a, b = m.groups()
            return (int(a), b.strip()) if i in (0, 3) else (int(b), a.strip())
    return 1, line.strip()


def _spell_scroll_line(name: str, spells) -> str | None:
    """"Scroll of Fireball", "Spell scroll: Bless", "Spell Scroll (Shield)",
    "Spell Scroll (1st level) — Bless" -> the app's bound scroll name
    ("Spell Scroll (3rd level) — Fireball"); None if it isn't one."""
    from .spell_scrolls import parse_spell_scroll, bound_scroll_name
    parsed = parse_spell_scroll(name)
    if parsed and parsed[1]:
        sp = _exact(parsed[1], spells)
        return bound_scroll_name(spells[sp].get("level", 0), sp) if sp else None
    m = re.match(r"^(?:spell\s+)?scroll\s*(?:of|:|-|—|–|\()\s*(?:the\s+)?(.+?)\)?$", name.strip(), re.I)
    if not m:
        return None
    sp = _exact(m.group(1), spells)
    if not sp:
        return None        # "Scroll of Protection" etc. -- a magic item, not a spell
    return bound_scroll_name(spells[sp].get("level", 0), sp)


def _loose_match(name: str, names):
    """"Hempen rope (50 feet)" -> "Rope, Hempen (50 ft)": same words in
    any order (feet/ft, plurals folded)."""
    def words(x):
        x = _norm(x).replace("feet", "ft").replace("foot", "ft")
        return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in x.split()}
    target = words(name)
    if not target:
        return None
    return next((n for n in names if words(n) == target), None)


def _item_catalogue():
    from dnd_app.data.phbCommon.items import WEAPON_DICT, ARMOR_DICT, ADVENTURING_GEAR, ALL_TOOLS
    weights = {}
    for n, d in WEAPON_DICT.items():
        weights[n] = float(d.get("weight", 0) or 0)
    for n, d in ARMOR_DICT.items():
        weights[n] = float(d.get("weight", 0) or 0)
    for row in ADVENTURING_GEAR:
        weights[row[0]] = float(row[1]) if len(row) > 1 and row[1] is not None else 0.0
    for t in ALL_TOOLS:
        weights.setdefault(t, 0.0)
    return weights


def _ability_scores(values: dict) -> tuple[dict, str]:
    """{ability: score} from the sheet's two boxes per ability. People
    write the score in either the big box or the small one (the official
    sheet is ambiguous about which is which), so it's worked out per
    ability: a score is always larger than its own modifier (even a 30's
    is +10), so of the two numbers the larger is the score. Where only one
    box is filled, the way round the other abilities were written decides;
    with nothing to go on, a number written with a sign (+3, -1) or of 5
    or less counts as a modifier. Abilities with only a modifier get an
    estimated score (10 + 2 x modifier) and the player is told."""
    def read(fid):
        raw = values.get(fid) if isinstance(values.get(fid), str) else ""
        n = _int(raw)
        return (n, bool(re.match(r"\s*[+\-\u2212]", raw or ""))) if n is not None else None

    pairs = {ab: (read(ABILITY_SCORE_FIELDS[ab]), read(ABILITY_MOD_FIELDS[ab])) for ab in ABILITIES}
    votes = {"big": 0, "small": 0}
    for big, small in pairs.values():
        if big and small and big[0] != small[0]:
            votes["big" if big[0] > small[0] else "small"] += 1
    lean = "big" if votes["big"] >= votes["small"] else "small"
    if not any(votes.values()):
        lean = None

    scores, estimated = {}, []
    for ab, (big, small) in pairs.items():
        if big and small:
            scores[ab] = max(big[0], small[0])
            continue
        one, box = (big, "big") if big else (small, "small")
        if not one:
            continue
        n, signed = one
        is_score = (box == lean) if lean else (not signed and n > 5)
        if is_score:
            scores[ab] = n
        else:
            scores[ab] = 10 + 2 * n
            estimated.append(ab)

    notes = []
    if votes["small"] > votes["big"]:
        notes.append("Ability scores were in the small boxes (modifiers in the big ones) -- read them that way round.")
    if estimated:
        notes.append(f"Only a modifier was written for {', '.join(estimated)}, so "
                     f"{'that score is an estimate' if len(estimated) == 1 else 'those scores are estimates'} "
                     "(10 + 2 x modifier) -- set the real score on the sheet.")
    if not scores:
        notes.append("No ability scores were found.")
    return {ab: n for ab, n in scores.items() if 1 <= n <= 30}, " ".join(notes)


# ── Building the character ───────────────────────────────────────────────
def character_from_values(values: dict, how: str = "form") -> tuple[dict, list[str]]:
    """(character dict, notes on what was and wasn't imported).

    `values` is {sheet field id: text, or True/False for a tick box}, from
    read_sheet_values(). In order:

      1. Identity -- name, race + subrace, background, alignment, XP, and
         each "Wizard 5 / Cleric 2" class with its level and subclass.
      2. Ability scores -- read from whichever box holds them
         (_ability_scores), then rebuild() so the race/class grants exist,
         and subtract the racial/ASI bonuses back out to get base scores.
      3. Proficiencies -- saves and skills from their tick boxes (or, on a
         flattened sheet, from the bonus being at least mod + proficiency);
         a skill bonus of mod + 2 x proficiency means expertise. Recorded
         as _choices so the next rebuild() keeps them. Languages, feats and
         fighting styles come from the text boxes.
      4. Spells -- each line on page 3 matched to a spell; cantrips vs
         levelled spells; ticked ones are prepared.
      5. Gear -- each Equipment line split into quantity + name, then:
         a spell scroll -> bound scroll; a catalogue item -> that item;
         "+1 Longsword" -> the base item plus an enchanted magic item;
         a magic item -> owned copy (attuned automatically if it needs it);
         anything else -> a custom item. Best armour and a shield go on.
      6. Money, personality, appearance and backstory.
      7. update_all() works out everything derived; then the sheet's own
         max HP (kept as an override if rolled), current HP, spent slots,
         hit dice and death saves are laid over the top.
      8. Checks -- AC and over-maximum scores that don't match what the
         app works out become notes, and every note plus any text that
         wasn't broken down goes on an "Imported from PDF" notes page."""
    from .character import new_character, ability_mod
    from .builder import rebuild
    from .calculator import update_all, get_prof_bonus, SKILL_ABILITY
    from .magic_items import add_owned_magic_item
    from dnd_app.data.phb2014.classes import CLASS_DICT
    from dnd_app.data.phbCommon.backgrounds import BACKGROUND_NAMES
    from dnd_app.data.phbCommon.feats import FEAT_NAMES
    from dnd_app.data.phbCommon.spells import SPELL_DICT
    from dnd_app.data.phbCommon.magic_items import MAGIC_ITEM_NAMES, get_magic_item
    from dnd_app.data.phbCommon.items import WEAPON_DICT
    from dnd_app.data.phbCommon.feature_ui_interactions import LANGUAGES

    v = lambda k: values.get(k) if isinstance(values.get(k), str) else ""
    checked = lambda k: values.get(k) is True
    report, leftovers = [], []

    char = new_character()
    char["name"] = (v("CharacterName") or v("CharacterName 2")).strip()
    char["player_name"] = v("PlayerName").strip()

    # identity
    race, subrace = _race_and_subrace(v("Race "))
    if race:
        char["race"], char["subrace"] = race, subrace
    elif v("Race ").strip():
        report.append(f"Race \"{v('Race ').strip()}\" isn't one this app knows -- pick it on the Race step.")
    bg = _exact(v("Background"), BACKGROUND_NAMES) or _best_match(v("Background"), BACKGROUND_NAMES)
    if bg:
        char["background"] = bg
    elif v("Background").strip():
        report.append(f"Background \"{v('Background').strip()}\" wasn't recognised.")
    al = v("Alignment").strip()
    char["alignment"] = ALIGNMENTS.get(al.lower()) or ALIGNMENTS.get(_norm(al)) or \
        next((a for a in ALIGNMENTS.values() if _norm(a) == _norm(al)), "True Neutral")
    char["experience"] = _int(v("XP"), 0) or 0
    char["inspiration"] = bool(v("Inspiration").strip())

    all_text = "\n".join(str(x) for x in values.values() if isinstance(x, str))
    classes = _classes(v("ClassLevel"))
    for cname, lvl in classes:
        hd = CLASS_DICT.get(cname, {}).get("hit_die", 8)
        char["classes"].append({"class": cname, "level": lvl, "hit_die": hd,
                                "subclass": _subclass_for(cname, v("ClassLevel") + "\n" + all_text)})
    if not classes:
        report.append("No class was found in CLASS & LEVEL -- add one before playing.")

    # ability scores as written (final, racial bonuses included)
    sheet_scores, note = _ability_scores(values)
    if note:
        report.append(note)
    char["abilities"].update(sheet_scores)

    choices = char["_choices"]
    rebuild(char)
    # put the racial/ASI bonuses back the other side: base = written - bonus
    for ab, score in sheet_scores.items():
        char["abilities"][ab] = max(1, score - char["ability_bonuses"].get(ab, 0))
    rebuild(char)
    for ab, score in sheet_scores.items():          # a cap trimmed a bonus
        diff = score - (char["abilities"][ab] + char["ability_bonuses"].get(ab, 0))
        if diff:
            char["abilities"][ab] += diff

    prof = get_prof_bonus(char)

    # saving throws: the boxes, or (flattened sheet) the bonus itself
    extra_saves = []
    for ab in ABILITIES:
        on = checked(SAVE_CHECKBOXES[ab])
        if how == "flattened":
            bonus = _int(v(SAVE_TEXT_FIELDS[ab]))
            on = bonus is not None and bonus - ability_mod(char, ab) >= prof
        if on and not char["saving_throws"].get(ab):
            extra_saves.append(ab)
    if extra_saves:
        choices["extra_save_profs"] = extra_saves

    # skills: the boxes for proficiency, the written bonus for expertise
    profs, experts = [], []
    for skill, text_id in SKILL_TEXT_FIELDS.items():
        ab = SKILL_ABILITY.get(skill)
        bonus = _int(v(text_id))
        over = (bonus - ability_mod(char, ab)) if (bonus is not None and ab) else None
        on = checked(SKILL_CHECKBOXES[skill]) or (over is not None and over >= prof)
        if over is not None and over >= 2 * prof:
            experts.append(skill)
        elif on:
            profs.append(skill)
    choices["class_skill_profs"] = sorted(set(profs + experts))
    if experts:
        choices["class_skill_expertise"] = experts

    # languages / tools from PROFICIENCIES & LANGUAGES
    langs = [l for l in LANGUAGES if re.search(rf"\b{re.escape(l)}\b", v("ProficienciesLang"), re.I)]
    if langs:
        choices["extra_languages"] = sorted(set(langs) | {"Common"})

    # feats and fighting styles named anywhere in Features & Traits
    feats_text = v("Features and Traits") + "\n" + v("Feat+Traits")
    for f in FEAT_NAMES:
        if re.search(rf"(?<![\w']){re.escape(f)}(?![\w'])", feats_text) and f not in char["feats"]:
            char["feats"].append(f)
    from dnd_app.data.phb2014.classes import FIGHTING_STYLES
    for raw in FIGHTING_STYLES:
        style = raw.split("\u2013")[0].split(" - ")[0].strip()
        if re.search(rf"fighting style[^\n]*\b{re.escape(style)}\b", feats_text, re.I):
            char.setdefault("fighting_styles", []).append(raw)

    rebuild(char)

    # spells (page 3)
    cantrips, known, prepared, unknown_spells = [], [], [], []
    for lvl, rows in SPELL_LEVEL_FIELDS.items():
        for text_id, check_id in rows:
            name = v(text_id).strip()
            if not name:
                continue
            match = _exact(name, SPELL_DICT) or _best_match(name, SPELL_DICT, min_len=4)
            if not match:
                unknown_spells.append(name)
                continue
            (cantrips if SPELL_DICT[match].get("level", 0) == 0 else known).append(match)
            if check_id and checked(check_id):
                prepared.append(match)
    char["cantrips"] = list(dict.fromkeys(cantrips))
    char["spells_known"] = list(dict.fromkeys(known))
    char["spells_prepared"] = list(dict.fromkeys(prepared))
    if unknown_spells:
        report.append("Spells not recognised: " + ", ".join(unknown_spells))
        leftovers.append("Spells: " + ", ".join(unknown_spells))

    # weapons, gear, magic items
    weights = _item_catalogue()
    weapon_rows = [v(n).strip() for n, _a, _d in WEAPON_FIELDS if v(n).strip()]
    eq_lines = _lines(v("Equipment"))
    if len(eq_lines) == 1 and "," in eq_lines[0]:
        eq_lines = [p.strip() for p in eq_lines[0].split(",") if p.strip()]
    unknown_items = []
    for line in eq_lines + weapon_rows:
        qty, name = _split_qty(line)
        scroll = _spell_scroll_line(name, SPELL_DICT)
        if scroll:
            # a spell scroll, bound to its spell ("Scroll of Fireball")
            existing = next((e for e in char["equipment"] if e["name"] == scroll), None)
            if existing:
                existing["qty"] += qty
            else:
                base = get_magic_item(scroll.split(" — ")[0]) or {}
                char["equipment"].append({"name": scroll, "qty": qty, "weight": 0.5, "notes": "",
                                          "magic": True, "rarity": base.get("rarity", "")})
            continue
        known_item = _exact(name, weights) or _exact(re.sub(r"s$", "", name), weights)
        mi = None if known_item else (_exact(name, MAGIC_ITEM_NAMES) or _loose_match(name, MAGIC_ITEM_NAMES))
        if mi and not known_item:
            if (get_magic_item(mi) or {}).get("type") in ("Potion", "Scroll"):
                char["equipment"].append({"name": mi, "qty": qty, "weight": 0.5, "notes": "", "magic": True,
                                          "rarity": get_magic_item(mi).get("rarity", "")})
            else:
                add_owned_magic_item(char, mi, qty)
            continue
        if not known_item:
            known_item = _loose_match(name, weights)
        # "+1 Longsword" / "Longsword +1": enchanted gear the way the app
        # tracks it -- the base item carried, plus a "Longsword +1" magic item
        plus = re.match(r"^\+([1-3])\s+(.+)$", name) or re.match(r"^(.+?)\s*\+([1-3])$", name)
        if plus and not known_item and not mi:
            bonus, base = (plus.group(1), plus.group(2)) if name.startswith("+") else (plus.group(2), plus.group(1))
            base = _exact(base, weights) or _loose_match(base, weights)
            from dnd_app.data.phbCommon.items import ARMOR_DICT as _AD
            if base and (base in WEAPON_DICT or base in _AD):
                enchanted = f"{base} +{bonus}"
                add_owned_magic_item(char, enchanted)
                if base in WEAPON_DICT:
                    char["equipped_weapons"].append(enchanted)
                elif _AD[base].get("type") == "shield":
                    char["shield"] = True
                    char["shield_magic_bonus"] = max(int(bonus), char.get("shield_magic_bonus", 0))
                else:
                    char["_imported_magic_armor"] = enchanted
                if not any(e["name"] == base for e in char["equipment"]):
                    char["equipment"].append({"name": base, "qty": 1, "weight": weights.get(base, 0.0), "notes": ""})
                continue
        item = known_item or name
        if not known_item:
            unknown_items.append(name)
        existing = next((e for e in char["equipment"] if e["name"] == item), None)
        if existing:
            if line not in weapon_rows:
                existing["qty"] += qty
        else:
            char["equipment"].append({"name": item, "qty": qty, "weight": weights.get(item, 0.0), "notes": ""})
        if line in weapon_rows and item in WEAPON_DICT and item not in char["equipped_weapons"]:
            char["equipped_weapons"].append(item)
    # magic items listed in Features & Traits (this app's own export puts them there)
    for line in _lines(v("Features and Traits")):
        name = re.sub(r"\s*\((attuned|equipped|attuned, equipped)\)$", "", line)
        mi = _exact(name, MAGIC_ITEM_NAMES) or _loose_match(name, MAGIC_ITEM_NAMES)
        if mi and not any(e["name"] == mi for e in char["magic_items"]):
            entry = add_owned_magic_item(char, mi)
            tagged = re.search(r"\((attuned|equipped|attuned, equipped)\)$", line)
            if tagged:
                # this app's own export says exactly what's attuned/equipped
                entry["_attune_known"] = True
                entry["equipped"] = "equipped" in tagged.group(1)
            if "attuned" in line:
                char.setdefault("attuned_items", []).append(mi)
                entry["attuned"] = True
    # a typed sheet rarely says what's attuned -- attune what needs it, up
    # to the limit, and say so
    from .magic_items import set_owned_magic_item_attuned
    auto = []
    for e in char["magic_items"]:
        if e.pop("_attune_known", False):
            continue
        if (get_magic_item(e["name"]) or {}).get("attunement") and not e.get("attuned"):
            if not set_owned_magic_item_attuned(char, e["uid"], True):
                auto.append(e["name"])
    if auto:
        report.append("Attuned to " + ", ".join(auto) + " (they need attunement) -- end it on the "
                      "Equipment screen for any you aren't attuned to.")
    if unknown_items:
        report.append("Added as custom items (not in the app's lists): " + ", ".join(unknown_items))

    # wear the best armour and a shield from what's carried
    from dnd_app.data.phbCommon.items import ARMOR_DICT
    owned = [e["name"] for e in char["equipment"]]
    armours = [n for n in owned if n in ARMOR_DICT and ARMOR_DICT[n].get("type") in ("light", "medium", "heavy")]
    if armours:
        char["armor_worn"] = max(armours, key=lambda n: ARMOR_DICT[n].get("ac", 0))
    if char.get("_imported_magic_armor"):
        char["armor_worn"] = char.pop("_imported_magic_armor")
    if any(n in ARMOR_DICT and ARMOR_DICT[n].get("type") == "shield" for n in owned):
        char["shield"] = True

    for c in ("CP", "SP", "EP", "GP", "PP"):
        char["currency"][c] = max(0, _int(v(c), 0) or 0)

    # personality, page 2
    for key, fid in (("personality_traits", "PersonalityTraits "), ("ideals", "Ideals"),
                     ("bonds", "Bonds"), ("flaws", "Flaws"), ("age", "Age"), ("height", "Height"),
                     ("weight", "Weight"), ("eyes", "Eyes"), ("skin", "Skin"), ("hair", "Hair"),
                     ("allies_and_organizations", "Allies"), ("backstory", "Backstory"),
                     ("treasure", "Treasure")):
        char[key] = v(fid).strip()
    char["additional_features"] = v("Feat+Traits").strip()

    # derive everything else (slots, resources, AC, hit dice...)
    update_all(char)

    # HP: the sheet's max (rolled HP differs from the average) and current
    hp_max = _int(v("HPMax"))
    if hp_max and hp_max > 0 and hp_max != char.get("max_hp"):
        char["hp_max_override"] = hp_max
        update_all(char)
    hp_cur = _int(v("HPCurrent"))
    char["current_hp"] = hp_cur if hp_cur is not None else char.get("max_hp", 0)
    char["temp_hp"] = max(0, _int(v("HPTemp"), 0) or 0)

    # spent slots / hit dice
    for lvl, (_total_id, used_id) in SLOT_FIELDS.items():
        used = _int(v(used_id))
        if used and lvl - 1 < len(char.get("spell_slots_used", [])):
            char["spell_slots_used"][lvl - 1] = min(used, char["spell_slots_max"][lvl - 1])
    hd_left = {f"d{d}": int(n) for n, d in re.findall(r"(\d+)\s*d\s*(\d+)", v("HD"))}
    for die, d in char.get("hit_dice", {}).items():
        if die in hd_left:
            d["remaining"] = min(d.get("total", 0), hd_left[die])
    char["death_saves"] = {
        "successes": sum(checked(b) for b in DEATH_SAVE_SUCCESS_CHECKBOXES),
        "failures": sum(checked(b) for b in DEATH_SAVE_FAILURE_CHECKBOXES),
    }

    # keep the free text this importer doesn't break down, word for word
    for label, fid in (("Features & Traits", "Features and Traits"),
                       ("Attacks & Spellcasting", "AttacksSpellcasting"),
                       ("Proficiencies & Languages", "ProficienciesLang")):
        if v(fid).strip():
            leftovers.append(f"{label}:\n{v(fid).strip()}")
    if unknown_items:
        leftovers.append("Equipment as written:\n" + v("Equipment").strip())

    # numbers worth checking: the sheet vs what the app works out
    from .character import ability_score as _score
    # the most a score can naturally be: 20, or 24 for a 20th-level
    # Barbarian's STR and CON (Primal Champion)
    primal = any(c["class"] == "Barbarian" and c["level"] >= 20 for c in char["classes"])
    cap = lambda ab: ((24 if primal and ab in ("STR", "CON") else 20)
                      + (char.get("ability_max_bonus") or {}).get(ab, 0))
    over = [f"{ab} {sc}" for ab, sc in sheet_scores.items() if sc > cap(ab) and _score(char, ab) < sc]
    if over:
        report.append(f"{', '.join(over)} {'is' if len(over) == 1 else 'are'} above the natural maximum -- "
                      "add the magic item or feature that raises it (e.g. a Belt of Giant Strength) "
                      "and the app will count it.")
    from .calculator import get_ac
    ac = _int(v("AC"))
    if ac and ac != get_ac(char):
        report.append(f"The sheet says AC {ac}, the app works out {get_ac(char)} -- check armour/shield.")
    if how == "flattened":
        report.append("This sheet was flattened, so its tick boxes couldn't be read -- proficiencies "
                      "were worked out from the bonuses; check death saves and prepared spells.")
    # the notes page: what to check, then the sheet's own words
    page = []
    if report:
        page.append("Things to check:\n" + "\n".join(f"- {r}" for r in report))
    page += leftovers
    if page:
        char["notes_pages"] = [{"title": "Imported from PDF", "text": "\n\n".join(page)}]
    return char, report


def import_character_pdf(path_or_stream) -> tuple[dict, list[str]]:
    """Read a filled official 5e sheet and build a character from it.
    Returns (character, notes for the player). Raises SheetImportError."""
    values, how = read_sheet_values(path_or_stream)
    return character_from_values(values, how)
