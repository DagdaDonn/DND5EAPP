"""
Apply magic item effects from data/magic_items.py onto character state.
All item definitions and effect payloads live in the data layer.
"""

from __future__ import annotations

from dnd_app.data.magic_items import get_item_effect, get_magic_item
import re as _re


def parse_magic_suffix(name: str) -> tuple[str, int]:
    """
    Split 'Longsword +1' -> ('Longsword', 1). Returns (name, 0) if no suffix.
    Recognizes a trailing ' +1', ' +2', or ' +3'.
    """
    m = _re.match(r'^(.*) \+([123])$', name.strip())
    if m:
        return m.group(1).strip(), int(m.group(2))
    return name, 0


def parse_material_prefix(name: str) -> tuple[str, str]:
    """
    Split 'Silvered Dagger' -> ('Dagger', 'Silvered'), or
    'Adamantine Longsword' -> ('Longsword', 'Adamantine').
    Returns (name, "") if no recognized prefix.

    Confirmed a real, significant bug this fixes: before this function
    existed, naming a weapon "Silvered X" or "Adamantine X" wasn't
    recognized by the weapon-name lookup at all (only the "+1"/"+2"/"+3"
    suffix was handled), so it silently fell through to the generic
    named-magic-weapon fallback and got corrupted stats — e.g. a
    Silvered Dagger would render with the fallback's flat 1d8 slashing
    damage and no properties, instead of the real dagger's 1d4
    piercing with Finesse/Light/Thrown.
    """
    stripped = name.strip()
    for prefix in ("Adamantine ", "Silvered "):
        if stripped.startswith(prefix):
            return stripped[len(prefix):].strip(), prefix.strip()
    return name, ""


def _active_item_names(char: dict) -> list[str]:
    """Items that apply mechanical effects: attuned items must ALSO be
    equipped (not just sitting attuned in a backpack — confirmed this
    was previously not checked at all for the attuned_items list, a
    real gap since the attunement toggle itself never required
    "equipped" either), and non-attunement items just need to be
    equipped."""
    names: list[str] = []
    attuned = set(char.get("attuned_items", []))
    equipped_lookup = {}
    for entry in char.get("magic_items", []):
        if isinstance(entry, dict):
            equipped_lookup[entry.get("name", "")] = entry.get("equipped", False)

    for n in attuned:
        if n and n not in names and equipped_lookup.get(n, False):
            names.append(n)

    for entry in char.get("magic_items", []):
        if isinstance(entry, str):
            name = entry
            entry = {"name": name, "equipped": True, "attunement": False}
        else:
            name = entry.get("name", "")
        if not name or name in names:
            continue
        if not entry.get("equipped", False):
            continue
        catalog = get_magic_item(name)
        requires_attune = bool(catalog.get("attunement")) if catalog else False
        if requires_attune:
            if name in attuned:
                names.append(name)
        else:
            names.append(name)
    return names


def reset_magic_item_modifiers(char: dict) -> None:
    """Clear transient modifiers before reapplying item effects."""
    char["ability_overrides"] = {}
    char["skill_advantages"] = []
    char["skill_disadvantages"] = []
    char["_skill_advantage_sources"] = {}     # {skill: [reason, ...]}
    char["_skill_disadvantage_sources"] = {}  # {skill: [reason, ...]}
    char["item_granted_spells"] = []
    char["item_spell_uses"] = {}
    char["item_actions"] = []
    char["item_granted_spell_details"] = []
    char["spell_dc_bonus"] = 0
    char["spell_attack_bonus"] = 0
    char["magic_ac_bonus"] = 0
    char["magic_save_bonus"] = 0
    char["magic_speed_bonus"] = 0
    char["_blackrazor_spellcasting"] = False
    char["_named_weapon_bonuses"] = {}  # {item_name: bonus_value}
    # Source-tracked breakdowns, used to build tooltips
    char["_ac_bonus_sources"] = []        # [(item_name, value), ...]
    char["_save_bonus_sources"] = []      # [(item_name, value), ...]
    char["_speed_bonus_sources"] = []     # [(item_name, value), ...]
    # Resistances / immunities granted by equipped+attuned items
    char["damage_resistances"] = []       # [(damage_type, item_name), ...]
    char["damage_immunities"] = []        # [(damage_type, item_name), ...]
    char["condition_immunities_magic"] = []  # [(condition, item_name), ...]
    char["advantage_saves_magic"] = []    # [(ability_or_'all', item_name), ...]


def apply_magic_item_effect(char: dict, item_name: str) -> None:
    """Apply a single item's effect to char (lookup from data)."""
    effect = get_item_effect(item_name)
    if not effect:
        return

    # An item can grant multiple simultaneous effects (e.g. an ability score
    # bonus AND a damage immunity) — represented as a list of effect dicts.
    if isinstance(effect, list):
        for sub_effect in effect:
            _apply_single_effect(char, item_name, sub_effect)
        return

    _apply_single_effect(char, item_name, effect)


def _apply_single_effect(char: dict, item_name: str, effect: dict) -> None:
    etype = effect["type"]
    if etype == "set_ability":
        ab = effect["ability"]
        val = effect["value"]
        overrides = char.setdefault("ability_overrides", {})
        current = overrides.get(ab, 0)
        overrides[ab] = max(current, val) if current else val

    elif etype == "skill_advantage":
        skills = char.setdefault("skill_advantages", [])
        sk = effect["skill"]
        if sk not in skills:
            skills.append(sk)
        char.setdefault("_skill_advantage_sources", {}).setdefault(sk, []).append(item_name)

    elif etype == "skill_disadvantage":
        skills = char.setdefault("skill_disadvantages", [])
        sk = effect["skill"]
        if sk not in skills:
            skills.append(sk)
        char.setdefault("_skill_disadvantage_sources", {}).setdefault(sk, []).append(item_name)

    elif etype == "grant_spell":
        # NOTE: item-granted spells are intentionally NOT added to spells_known —
        # they appear only in the Action/Bonus Action/Reaction quick-access tabs,
        # since they're cast via the item, not part of the character's own
        # spell list or spellbook.
        spell = effect["spell"]
        granted = char.setdefault("item_granted_spells", [])
        if spell not in granted:
            granted.append(spell)
        uses = effect.get("uses", 0)
        if uses:
            char.setdefault("item_spell_uses", {})[spell] = uses
        # Track per-item metadata so the action tabs can build a proper row
        char.setdefault("item_granted_spell_details", []).append({
            "spell": spell,
            "source": item_name,
            "uses": uses,
            "recharge": effect.get("recharge", "dawn"),
            "action_type": effect.get("action_type", "Action"),
            "dc": effect.get("dc"),
        })

    elif etype == "grant_action":
        actions = char.setdefault("item_actions", [])
        actions.append({
            "name": effect.get("action", "Special"),
            "source": item_name,
            "description": effect.get("description", ""),
            "action_type": effect.get("action_type", "Passive"),
        })
        if effect.get("spellcasting_weapon"):
            char["_blackrazor_spellcasting"] = True

    elif etype == "spell_dc_bonus":
        char["spell_dc_bonus"] = char.get("spell_dc_bonus", 0) + effect.get("value", 0)
        # Some items (Rod of Pact Keeper, Wand of War Mage) also boost spell attack
        atk = effect.get("atk_bonus", 0)
        if atk:
            char["spell_attack_bonus"] = char.get("spell_attack_bonus", 0) + atk

    elif etype == "spell_attack_bonus":
        char["spell_attack_bonus"] = char.get("spell_attack_bonus", 0) + effect.get("value", 0)

    elif etype == "ac_bonus":
        val = effect.get("value", 0)
        char["magic_ac_bonus"] = char.get("magic_ac_bonus", 0) + val
        char.setdefault("_ac_bonus_sources", []).append((item_name, val))
        # Some items give both AC and save bonus (Cloak/Ring of Protection)
        sb = effect.get("save_bonus", 0)
        if sb:
            char["magic_save_bonus"] = char.get("magic_save_bonus", 0) + sb
            char.setdefault("_save_bonus_sources", []).append((item_name, sb))

    elif etype == "save_bonus":
        val = effect.get("value", 0)
        char["magic_save_bonus"] = char.get("magic_save_bonus", 0) + val
        char.setdefault("_save_bonus_sources", []).append((item_name, val))

    elif etype == "weapon_damage_bonus":
        char.setdefault("_weapon_damage_bonuses", []).append({
            "source": item_name,
            "weapon_type": effect.get("weapon_type", ""),
            "value": effect.get("value", 0),
        })

    elif etype == "weapon_attack_bonus":
        # A named magic weapon grants +N to attack AND damage when equipped.
        # Store keyed by item_name so the weapon row can look it up.
        val = effect.get("value", 0)
        if val > 0:
            char.setdefault("_named_weapon_bonuses", {})[item_name] = val

    elif etype == "resistance":
        dmg_type = effect.get("damage_type", "")
        char.setdefault("damage_resistances", []).append((dmg_type, item_name))

    elif etype == "immunity":
        dmg_type = effect.get("damage_type", "")
        char.setdefault("damage_immunities", []).append((dmg_type, item_name))

    elif etype == "resistance_choice":
        # The specific damage type is fixed per-copy of the item (set when
        # it was created/found), represented here as a one-time player
        # choice rather than a guessed default. No resistance is applied
        # until the player actually picks one via the item's row in the
        # Gear tab.
        picks = char.get("_choices", {}).get(f"item_dmgtype_{item_name}", [])
        if picks:
            char.setdefault("damage_resistances", []).append((picks[0].lower(), item_name))

    elif etype == "condition_immunity":
        cond = effect.get("condition", "")
        char.setdefault("condition_immunities_magic", []).append((cond, item_name))

    elif etype == "speed_bonus":
        val = effect.get("value", 0)
        char["magic_speed_bonus"] = char.get("magic_speed_bonus", 0) + val
        char.setdefault("_speed_bonus_sources", []).append((item_name, val))

    elif etype == "min_speed":
        # "Your speed becomes X, unless it's already higher" (Boots of Striding, etc.)
        floor = effect.get("value", 0)
        base_speed = char.get("speed", 30)
        if base_speed < floor:
            bump = floor - base_speed
            char["magic_speed_bonus"] = char.get("magic_speed_bonus", 0) + bump
            char.setdefault("_speed_bonus_sources", []).append((item_name, bump))

    elif etype == "advantage_save":
        ability = effect.get("ability", "all")
        char.setdefault("advantage_saves_magic", []).append((ability, item_name))


def apply_equipment_skill_effects(char: dict) -> None:
    """
    Apply baseline equipment rules that grant advantage/disadvantage on
    specific skills — distinct from magic item effects, since these come
    from mundane armor properties (PHB p.144: armor that imposes Stealth
    disadvantage does so for ANY wearer, not just magic armor).
    """
    from dnd_app.data.items import ARMOR_DICT

    armor_name = char.get("armor_worn", "No Armor")
    base_armor_name, _ = parse_magic_suffix(armor_name)
    armor = ARMOR_DICT.get(base_armor_name)
    if armor and armor.get("stealth"):
        dis = char.setdefault("skill_disadvantages", [])
        if "Stealth" not in dis:
            dis.append("Stealth")
        char.setdefault("_skill_disadvantage_sources", {}).setdefault("Stealth", []).append(
            f"{base_armor_name} (armor imposes Stealth disadvantage)"
        )


def _is_infusion_target_equipped(char: dict, target_item: str, infusion_name: str) -> bool:
    """Whether the specific item an infusion was applied to is actually
    equipped right now, using the correct mechanism for its slot type
    (weapon/armor/shield each track "equipped" completely differently).
    Confirmed this check didn't exist anywhere before — infusion-based
    charge items had no equip-prerequisite enforcement at all."""
    from dnd_app.data.classes import ARTIFICER_INFUSION_TARGETS
    target_type = ARTIFICER_INFUSION_TARGETS.get(infusion_name)
    if target_type == "weapon":
        return target_item in char.get("equipped_weapons", [])
    if target_type == "armor":
        return char.get("armor_worn", "No Armor") == target_item
    if target_type == "shield":
        return bool(char.get("shield", False))
    if target_type == "armor_or_shield":
        return (char.get("armor_worn", "No Armor") == target_item
                or bool(char.get("shield", False)))
    return True  # standalone infusions have no separate equip check


def sync_item_charges(char: dict) -> None:
    """
    Ensure every active item with a chargeable grant_spell effect has a
    tracked entry in char['item_charges']. Existing current values are
    preserved across refreshes (so spending charges sticks); only the max
    and recharge condition are kept in sync with the catalog.

    Also covers infusion-based charge items (Armor of Magical Strength,
    Mind Sharpener, Radiant Weapon, Repulsion Shield) — confirmed these
    had zero charge tracking at all, a completely separate data path
    from the catalog-based magic_items system since they enchant an
    existing equipment item rather than creating a standalone entry.
    Correctly requires the specific infused item to be equipped (not
    just the infusion being known/active), using each slot type's real
    equipped-status mechanism.
    """
    tracked = char.setdefault("item_charges", {})
    active = set(_active_item_names(char))

    for name in active:
        effect = get_item_effect(name)
        if not effect:
            continue
        effect_list = effect if isinstance(effect, list) else [effect]
        for sub in effect_list:
            if sub.get("type") != "grant_spell":
                continue
            uses = sub.get("uses", 0)
            if not uses:
                continue
            recharge = sub.get("recharge", "dawn")
            existing = tracked.get(name)
            if existing:
                existing["max"] = uses
                existing["recharge"] = recharge
                existing["current"] = min(existing.get("current", uses), uses)
            else:
                tracked[name] = {"current": uses, "max": uses, "recharge": recharge}

    from dnd_app.data.classes import ARTIFICER_INFUSION_CHARGES
    infusion_charge_keys = set()
    for inf in char.get("active_infusions", []):
        name = inf.get("infusion", "")
        charge_info = ARTIFICER_INFUSION_CHARGES.get(name)
        if not charge_info:
            continue
        target_item = inf.get("target_item")
        if not target_item or not _is_infusion_target_equipped(char, target_item, name):
            continue
        max_charges, recharge_dice, recharge_timing = charge_info
        key = f"{name} ({target_item})"
        infusion_charge_keys.add(key)
        existing = tracked.get(key)
        if existing:
            existing["max"] = max_charges
            existing["recharge"] = recharge_timing
            existing["current"] = min(existing.get("current", max_charges), max_charges)
        else:
            tracked[key] = {"current": max_charges, "max": max_charges, "recharge": recharge_timing}

    # Drop tracking for items no longer active, so removed/unattuned items
    # don't linger in the Other tab.
    for stale in [n for n in tracked if n not in active and n not in infusion_charge_keys]:
        del tracked[stale]


def apply_all_magic_item_effects(char: dict) -> None:
    """Reapply all magic item effects from attuned/equipped items."""
    reset_magic_item_modifiers(char)
    for name in _active_item_names(char):
        apply_magic_item_effect(char, name)
    apply_equipment_skill_effects(char)
    sync_item_charges(char)
    _apply_infusion_bonuses(char)


def _apply_infusion_bonuses(char: dict) -> None:
    """Apply the numerical bonus from standalone-target Artificer
    infusions (Enhanced Arcane Focus -> spell attack, Enhanced Defense/
    Repulsion Shield -> AC). Confirmed via direct testing these were
    never applied anywhere at all — the magic item catalog entries for
    them are flavor text only with no effects list, and unlike weapon
    infusions they don't get a "+N" name suffix to parse. Weapon-
    targeting infusions (Enhanced Weapon, Radiant Weapon, Repeating
    Shot, Returning Weapon) are handled separately at the point each
    weapon row is built, since their bonus is per-weapon, not global."""
    from .calculator import get_infusion_bonus, class_levels
    art_lvl = class_levels(char).get("Artificer", 0)
    for inf in char.get("active_infusions", []):
        name = inf.get("infusion", "")
        bonus = get_infusion_bonus(name, art_lvl)
        if not bonus:
            continue
        if name == "Enhanced Arcane Focus":
            char["spell_attack_bonus"] = char.get("spell_attack_bonus", 0) + bonus
        elif name in ("Enhanced Defense", "Repulsion Shield (+1)"):
            char["magic_ac_bonus"] = char.get("magic_ac_bonus", 0) + bonus


def concentration_save(char: dict, damage: int) -> tuple[bool, int]:
    """
    Roll concentration save after taking damage.
    Returns (maintained, roll_total).
    """
    import random
    from .calculator import get_saving_throw_bonus

    conc = char.get("concentration", {})
    if not conc or not conc.get("spell"):
        return True, 0

    dc = max(10, damage // 2)
    con_save = get_saving_throw_bonus(char, "CON")
    # War Caster: advantage on CON saves made to maintain concentration.
    # Previously this always rolled a single flat d20 with no advantage
    # mechanism at all, so the feat's actual core benefit never applied.
    if "War Caster" in char.get("feats", []):
        roll = max(random.randint(1, 20), random.randint(1, 20))
    else:
        roll = random.randint(1, 20)
    total = roll + con_save
    if total >= dc:
        return True, total
    conc["spell"] = None
    conc["since_round"] = 0
    return False, total


def start_concentration(char: dict, spell_name: str, *, round_num: int = 0) -> None:
    char.setdefault("concentration", {"spell": None, "since_round": 0})
    char["concentration"]["spell"] = spell_name
    char["concentration"]["since_round"] = round_num


def drop_concentration(char: dict) -> None:
    conc = char.setdefault("concentration", {"spell": None, "since_round": 0})
    conc["spell"] = None
    conc["since_round"] = 0
