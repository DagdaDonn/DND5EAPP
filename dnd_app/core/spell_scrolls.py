"""
Spell scrolls (DMG p.200): every scroll carries one specific spell.

Owned scrolls are equipment entries named "Spell Scroll (3rd level) — Fireball".
A bare "Spell Scroll (3rd level)" (an older save, a PDF import) has no spell
yet -- the UIs ask for one before it can be used, and bind_spell_scroll()
gives that one copy its spell.

Using a scroll casts its spell: no slot and no material components, and it
uses the scroll's own save DC / attack bonus (the table below), not yours.
  * The spell must be on one of your classes' spell lists (or one you know /
    have prepared, which covers domain and other expanded lists) -- otherwise
    the scroll is unintelligible, and it isn't used up.
  * If the spell is of a higher level than you can normally cast, you make an
    ability check with your spellcasting ability, DC 10 + the spell's level;
    on a failure the spell vanishes from the scroll with no other effect.
  * A Thief rogue's Use Magic Device (13th level) ignores the class-list
    requirement, checking with Intelligence.
"""
from __future__ import annotations

import random
import re

_SCROLL_RE = re.compile(r"^Spell Scroll \((Cantrip|(\d)(?:st|nd|rd|th) level)\)(?:\s*[—–-]\s*(.+))?$")

# DMG Spell Scroll table: spell level -> (save DC, attack bonus)
SCROLL_STATS = {0: (13, 5), 1: (13, 5), 2: (13, 5), 3: (15, 7), 4: (15, 7),
                5: (17, 9), 6: (17, 9), 7: (18, 10), 8: (18, 10), 9: (19, 11)}

# third casters read from the wizard's list
_LIST_FOR = {"Fighter": "Wizard", "Rogue": "Wizard"}
_THIRD_CASTER_SUBCLASS = {"Fighter": "eldritch knight", "Rogue": "arcane trickster"}


def parse_spell_scroll(name: str):
    """(spell level, spell name or None) for a spell scroll, else None."""
    m = _SCROLL_RE.match((name or "").strip())
    if not m:
        return None
    level = 0 if m.group(1) == "Cantrip" else int(m.group(2))
    return level, (m.group(3) or "").strip() or None


def scroll_base_name(level: int) -> str:
    if level == 0:
        return "Spell Scroll (Cantrip)"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(level, "th")
    return f"Spell Scroll ({level}{suffix} level)"


def bound_scroll_name(level: int, spell: str) -> str:
    return f"{scroll_base_name(level)} — {spell}"


def spell_for_scroll_level(level: int) -> list[str]:
    from dnd_app.data.phbCommon.spells import SPELLS_BY_LEVEL
    return sorted(s["name"] for s in SPELLS_BY_LEVEL.get(level, []))


def bind_spell_scroll(char: dict, eq_name: str, spell: str) -> str | None:
    """Give one blank scroll from the stack `eq_name` its spell. Returns the
    bound scroll's equipment name (None if it couldn't)."""
    parsed = parse_spell_scroll(eq_name)
    from dnd_app.data.phbCommon.spells import get_spell
    data = get_spell(spell)
    if not parsed or parsed[1] or not data or data.get("level") != parsed[0]:
        return None
    eq = char.setdefault("equipment", [])
    entry = next((e for e in eq if isinstance(e, dict) and e.get("name") == eq_name), None)
    if not entry:
        return None
    new_name = bound_scroll_name(parsed[0], spell)
    if entry.get("qty", 1) > 1:
        entry["qty"] -= 1
        same = next((e for e in eq if isinstance(e, dict) and e.get("name") == new_name), None)
        if same:
            same["qty"] = same.get("qty", 1) + 1
        else:
            copy = {k: v for k, v in entry.items() if k != "qty"}
            copy.update({"name": new_name, "qty": 1})
            eq.append(copy)
    else:
        same = next((e for e in eq if isinstance(e, dict) and e.get("name") == new_name), None)
        if same:
            same["qty"] = same.get("qty", 1) + 1
            eq.remove(entry)
        else:
            entry["name"] = new_name
    return new_name


def _highest_castable_level(char: dict) -> int:
    slots = char.get("spell_slots_max", []) or []
    best = max((i + 1 for i, n in enumerate(slots) if n), default=0)
    if char.get("pact_slots_max"):
        best = max(best, char.get("pact_slot_level", 0) or 0)
    return best


def scroll_reading(char: dict, spell_name: str) -> dict:
    """Whether this character can use a scroll of `spell_name`, and how:
    {"readable", "reason", "check": None or {"ability", "mod", "dc"},
     "save_dc", "attack", "level"}.

      save DC / attack come from the scroll's level (SCROLL_STATS)
      find a class whose spell list has it (Eldritch Knight / Arcane
        Trickster use the wizard's list) -> that class's casting ability
      else a spell you already know or have prepared (domain and other
        expanded lists) -> your usual casting ability
      else a 13th-level Thief (Use Magic Device) -> Intelligence
      else -> not readable
      readable, but above the highest slot level you have -> an ability
        check is needed, DC 10 + spell level"""
    from dnd_app.data.phbCommon.spells import get_spell, CLASS_SPELLS
    from dnd_app.data.phb2014.classes import CLASS_DICT
    from .character import ability_mod
    spell = get_spell(spell_name) or {}
    level = spell.get("level", 0)
    save_dc, attack = SCROLL_STATS.get(level, (13, 5))
    out = {"readable": False, "reason": "", "check": None, "save_dc": save_dc,
           "attack": attack, "level": level}
    if not spell:
        out["reason"] = f"{spell_name} isn't a spell this app knows."
        return out

    ability = None
    for c in char.get("classes", []):
        cname = c.get("class", "")
        list_name = cname
        if cname in _LIST_FOR:
            if _THIRD_CASTER_SUBCLASS[cname] not in (c.get("subclass") or "").lower():
                continue
            list_name = _LIST_FOR[cname]
        names = {s["name"] for s in CLASS_SPELLS.get(list_name, [])}
        if spell_name in names:
            ability = CLASS_DICT.get(cname, {}).get("spell_ability") or "INT"
            break
    if ability is None and spell_name in (set(char.get("spells_known", [])) | set(char.get("cantrips", []))
                                          | set(char.get("spells_prepared", []))):
        from .calculator import _detect_spell_ability
        ability = _detect_spell_ability(char) or "INT"
    thief = any(c.get("class") == "Rogue" and c.get("level", 0) >= 13
                and "thief" in (c.get("subclass") or "").lower() for c in char.get("classes", []))
    if ability is None and thief:
        ability = "INT"
    if ability is None:
        out["reason"] = (f"{spell_name} isn't on your class's spell list -- the scroll is "
                         "unintelligible to you.")
        return out

    out["readable"] = True
    if level > _highest_castable_level(char) and level > 0:
        out["check"] = {"ability": ability, "mod": ability_mod(char, ability), "dc": 10 + level}
    return out


def use_spell_scroll(char: dict, eq_name: str, rng=random) -> dict:
    """Read one scroll from the stack `eq_name`. Returns
    {"status": "cast" | "failed" | "unreadable" | "unbound" | "missing",
     "spell", "message", "save_dc", "attack", "roll"}. The scroll is used up
    on "cast" and "failed"; the caller applies the cast itself (concentration,
    effects, the turn tracker) on "cast".

      not a spell scroll, or not owned          -> "missing"
      no spell written on it yet               -> "unbound" (the UI asks
                                                   which spell, binds, retries)
      spell not on any of your lists           -> "unreadable", scroll kept
      spell above the level you can cast:
        roll d20 + spellcasting mod vs 10 + spell level
          below -> "failed", scroll used up, no effect
          else  -> "cast", scroll used up
      otherwise                                -> "cast", scroll used up"""
    parsed = parse_spell_scroll(eq_name)
    eq = char.get("equipment", [])
    entry = next((e for e in eq if isinstance(e, dict) and e.get("name") == eq_name), None)
    if not parsed or not entry:
        return {"status": "missing", "message": f"{eq_name} isn't in your inventory."}
    level, spell = parsed
    if not spell:
        return {"status": "unbound", "level": level,
                "message": "This scroll has no spell written on it yet -- choose one first."}
    info = scroll_reading(char, spell)
    res = {"spell": spell, "save_dc": info["save_dc"], "attack": info["attack"], "roll": None}
    if not info["readable"]:
        return {**res, "status": "unreadable", "message": info["reason"]}

    def consume():
        entry["qty"] = entry.get("qty", 1) - 1
        if entry["qty"] <= 0:
            char["equipment"] = [e for e in eq if e is not entry]

    stats = f"save DC {info['save_dc']}, +{info['attack']} to hit"
    if info["check"]:
        chk = info["check"]
        d20 = rng.randint(1, 20)
        total = d20 + chk["mod"]
        res["roll"] = {"d20": d20, "total": total, "dc": chk["dc"], "ability": chk["ability"]}
        roll_txt = f"{chk['ability']} check {d20}{chk['mod']:+d} = {total} vs DC {chk['dc']}"
        if total < chk["dc"]:
            consume()
            return {**res, "status": "failed",
                    "message": f"{roll_txt} -- failed. The spell fades from the scroll with no effect."}
        consume()
        return {**res, "status": "cast",
                "message": f"{roll_txt} -- success! Cast {spell} from the scroll ({stats})."}
    consume()
    return {**res, "status": "cast", "message": f"Cast {spell} from the scroll ({stats})."}
