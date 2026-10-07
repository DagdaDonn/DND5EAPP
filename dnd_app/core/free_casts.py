"""Free daily casts -- spells a race, feat or feature lets you cast without a
spell slot, a set number of times between rests (a Tiefling's Hellish
Rebuke once per long rest, Fey Touched's Misty Step, Firbolg Magic...).

Each source is a tracked resource in char["resources"] (shown with the
other limited-use features, reset by the matching rest). This module
answers two questions for the Cast button on both apps:
  1. Which spells can this resource cast?  free_spells_of()
  2. Is there a free use of this spell left, and spend it.  spend_free_cast()

How a resource names its spells:
  - an explicit "free_spells" list (the resources built here), or
  - for older resources, the spell names in its note after "Cast ..."
    ("Cast misty step and tongues, each once, without a spell slot."), or
  - a feat whose spell is the player's pick (Magic Initiate) reads it
    back from _choices.
"""
import re

# Racial spells that are NOT a limited free cast (at will, or only in a
# narrow case), so they get no counter: {(race prefix, spell)}
_NOT_DAILY = {
    ("Yuan-ti", "Animal Friendship"),   # at will, on snakes only
}

# Extra wording for a free cast that isn't quite the plain spell.
_CAST_NOTES = {
    ("Tiefling", "Hellish Rebuke"): "cast as a 2nd-level spell",
}

# Resources whose spell is the player's pick: {resource key: _choices key}
_CHOSEN_SPELL_RESOURCES = {
    "magic_initiate": "feat_magic_initiate_spell",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def free_spells_of(char: dict, resource: dict) -> list[str]:
    """The spells `resource` lets the character cast for free."""
    if resource.get("free_spells"):
        return list(resource["free_spells"])
    choice_key = _CHOSEN_SPELL_RESOURCES.get(resource.get("key", ""))
    if choice_key:
        return list(char.get("_choices", {}).get(choice_key, []))
    note = resource.get("note", "")
    m = re.search(r"\bcast\s+(.*?)(?:\swithout\b|\susing\b|\(|\.\s|$)", note, re.IGNORECASE)
    if not m:
        return []
    named = m.group(1).lower()
    from dnd_app.data.phbCommon.spells import SPELL_NAMES
    # longest names first, so "Greater Invisibility" isn't also read as "Invisibility"
    found = []
    for name in sorted(SPELL_NAMES, key=len, reverse=True):
        pat = r"(?<![a-z])" + re.escape(name.lower()) + r"(?![a-z])"
        if re.search(pat, named):
            found.append(name)
            named = re.sub(pat, " ", named)
    return found


def free_cast_resources(char: dict, spell_name: str) -> list[dict]:
    """Resources with a use left that can cast `spell_name` for free."""
    return [r for r in char.get("resources", [])
            if r.get("current", 0) > 0 and spell_name in free_spells_of(char, r)]


def spend_free_cast(char: dict, spell_name: str):
    """Use one free cast of `spell_name` if there is one; returns the
    resource it came from (or None, and nothing changes)."""
    options = free_cast_resources(char, spell_name)
    if not options:
        return None
    res = options[0]
    res["current"] = res.get("current", 0) - 1
    return res


def reset_phrase(resource: dict) -> str:
    """'long rest' / 'short or long rest', for messages."""
    return "short or long rest" if "SR" in resource.get("reset", "LR") else "long rest"


def free_cast_message(spell_name: str, resource: dict) -> str:
    """The toast after a free cast, e.g. "Cast Darkness for free (Tiefling)
    -- no free casts left until a long rest"."""
    source = resource.get("name", "")
    if "(" in source and source.endswith(")"):
        source = source[source.rfind("(") + 1:-1]      # "Darkness (Tiefling)" -> "Tiefling"
    left = resource.get("current", 0)
    tail = (f"{left} free cast{'s' if left != 1 else ''} left" if left
            else f"no free casts left until a {reset_phrase(resource)}")
    return f"Cast {spell_name} for free ({source}) -- {tail}"


def innate_free_cast_resources(char: dict, existing: list) -> list[dict]:
    """New counters for free casts nothing else tracks yet: each leveled
    racial spell (once per long rest), and Fey Touched / Shadow Touched's
    two spells (each once per long rest). A spell already covered by an
    existing resource (Firbolg Magic, Yuan-ti Suggestion...) is skipped,
    so no spell gets two counters."""
    from dnd_app.data.phbCommon.spells import (get_spell, racial_innate_spells,
                                               FEAT_FIXED_SPELLS, FEAT_CHOSEN_SPELL_KEYS)
    covered = {sp for r in existing for sp in free_spells_of(char, r)}
    species = char.get("species") or char.get("race", "")
    out = []

    def _add(spell, source, key_prefix, note_extra=""):
        sp = get_spell(spell)
        if not sp or sp.get("level", 0) == 0 or spell in covered:
            return   # cantrips are at will; one counter per spell
        covered.add(spell)
        note = f"Cast {spell} once without a spell slot ({source})"
        note += f", {note_extra}." if note_extra else "."
        out.append({
            "name": f"{spell} ({source})", "key": f"{key_prefix}_{_slug(spell)}",
            "reset": "LR", "current_max": 1, "track": "uses",
            "note": note, "free_spells": [spell],
            "source_class": "", "subclass": "",
        })

    for spell in racial_innate_spells(char):
        race_prefix = next((r for (r, s) in _NOT_DAILY if species.startswith(r) and s == spell), None)
        if race_prefix:
            continue
        extra = next((n for (r, s), n in _CAST_NOTES.items() if species.startswith(r) and s == spell), "")
        _add(spell, species or "racial", "free_racial", extra)

    choices = char.get("_choices", {})
    for feat in ("Fey Touched", "Shadow Touched"):
        if feat not in char.get("feats", []):
            continue
        spells = list(FEAT_FIXED_SPELLS.get(feat, []))
        for key in FEAT_CHOSEN_SPELL_KEYS.get(feat, []):
            spells.extend(choices.get(key, []))
        for spell in spells:
            _add(spell, feat, f"free_{_slug(feat)}")
    return out
