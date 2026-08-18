# 🎲 MIMIC

### *A Complete D&D 5e Character Creator & Management Tool*

**MIMIC** is a desktop application for Dungeons & Dragons 5th Edition that puts everything you need in one place — races, classes, subclasses, spells, feats, backgrounds, magic items, companions, wild shape, combat tracking, and more. All offline, all free, all in a single portable executable.

> *"It looks like a character builder... or is it?"*

---

## 📦 What's Included

### Core Database
- **85 races** with subraces from every official sourcebook, including modern (MPMM) revisions kept alongside their original printings where the two differ mechanically
- **138 feats** from PHB (2014 & 2024), XGE, TCE, FTD, and more
- **99 backgrounds** from PHB (2014), plus adventure-specific backgrounds — 2024 Origin Feat backgrounds intentionally excluded, since this app targets the 2014 ruleset only
- **14 classes** including Blood Hunter
- **126 subclass combinations** (2014 ruleset) — audited line-by-line against source text, not filled in from memory
- **508 spells** across all 9 levels with per-class spell lists
- **856 magic items**, with real mechanical effects (ability score overrides, resistances, weapon bonuses) for a growing subset rather than description-only text
- **All standard weapons and armor** with computed attack bonuses and damage, plus **browsable Silvered and Adamantine variants** of every weapon (correctly restricted to melee weapons only for Adamantine, per the real rule) with accurate cost surcharges and the real mechanical text for each
- **28-beast Wild Shape catalog** spanning CR ¼ through CR 6, filtered by your actual druid level and any race/beast restrictions
- **Full companion stat blocks** for Steel Defender, Wildfire Spirit, Drake Companion, Dancing Item, Primal Companions (Beast of the Land/Sea/Sky), and Eldritch Cannon
- **11 races with real natural weapons** (Aarakocra Talons, Tabaxi Claws, Lizardfolk Bite, Minotaur Horns, Satyr Ram, Longtooth Shifter's Fangs, and more) rendered as actual weapon rows with computed attack and damage — not just flavor text, and correctly covering both original and MPMM printings where a race has both

### Character Builder
- **Full Character Creation Wizard:** Race → Ability Scores → Background & Class → Spells → Equipment
- **Point Buy, Standard Array, or Manual Entry** for ability scores
- **Live race detail panel** — picking a subrace updates the shown ASI and traits immediately, not just at the end
- **Full background details** — feature descriptions, bonus languages, and starting equipment shown in full, not truncated
- **Starting equipment picker** with class-appropriate options — every chosen item (armor, weapons, and a chosen equipment pack's real individual contents) lands correctly in your actual inventory, alongside your background's own equipment and starting gold
- **Level-up wizard** — walks through each level's choices, including nested sub-choices (like Aspect of the Beast's Tiger option, which itself grants a further skill pick)
- **Multiclassing support** — full rules for combining classes

### Spell Management
- **Prepared/known spell tracking** — mark spells as prepared or known
- **Spell slots by level** — automatically calculated and tracked
- **Concentration tracking** — with save prompts when you take damage
- **Ritual and quick-cast markers** — identify spells at a glance
- **Searchable spell browser** — find any spell instantly
- **Auto-prepared spells** for domains, oaths, and circles with a verified spell list (currently covers Cleric's Knowledge/Ambition/Solidarity/Strength/Zeal Domains, all 8 Circle of the Land terrains, and 3 Paladin oaths — more added as each subclass's spell list is checked against source)
- **Spell descriptions on hover** — tooltips for every spell

### Optional Class Features
- **Eldritch Invocations** — all 54 real options, individually wired with real mechanics (spell grants, resources, Known Actions entries, or passive effects as each actually requires), correctly gated by level, Pact Boon, and spell prerequisites (like requiring Eldritch Blast or Hex) rather than showing every option regardless of eligibility
- **Battle Master Maneuvers, Metamagic, Fighting Styles, and Artificer Infusions** — every real option audited and wired, including subtler ones like Resistant Armor's actual choosable damage resistance
- **Elemental Disciplines, Arcane Shot, and Rune Knight Runes** — fully wired, correctly showing your chosen options as real, usable entries rather than passive text
- **Eldritch Adept, Metamagic Adept, and Martial Adept feats** — grant a real choice of invocation/metamagic/maneuver, not just the underlying resource
- **Eldritch Versatility** — swap a cantrip, your Pact Boon, or a Mystic Arcanum spell at the right levels, with any now-ineligible invocation correctly flagged for replacement

### Combat Tracker
- **Full HP tracking** — Max, Current, and Temporary HP with one-click damage/heal
- **Max HP override** — with reset-to-calculated button
- **Turn tracker** — Action, Bonus Action, and Reaction economy with one-click New Turn reset
- **Known Actions filter** — every real, usable action, filterable by Common/Race/Spell (Magic Item filter category reserved for when that system gets full mechanical wiring), with a further level sub-filter (Cantrip through 9th) when viewing spells, so a full spellbook doesn't flood the page
- **Casting a spell correctly consumes the right action-economy slot** — cantrips and leveled spells alike, based on each spell's real casting time (Action, Bonus Action, or Reaction), with longer ritual/utility casts correctly exempted
- **The real "one leveled spell per turn" rule enforced** — casting a spell with a bonus action correctly restricts the only other spell castable that turn to a cantrip, checked in both directions (whichever slot is used first), with Haste's genuine extra action correctly recognized as an exception
- **Casting a spell that matches an existing buff/condition system automatically applies it** — Bless, Haste, Shield of Faith, and more, with a self-vs-another prompt for spells that could target either
- **Class resource tracking** — Rage, Ki, Sorcery Points, Superiority Dice, Channel Divinity, and every other class resource
- **Short and long rest auto-reset** — all resources recharge correctly
- **Death saves, conditions checklist, and exhaustion tracking**
- **Weapon and armor equipping** with computed attack bonuses and damage
- **On-hit damage bonuses shown separately by type** — Divine Strike, Improved Divine Smite, Genie's Wrath, Dreadful Strikes, Aura of Hate, and weapon-specific item bonuses (like Bracers of Archery) each appear as their own badge next to a weapon, rather than folded into one number — since a different damage type genuinely matters against resistance/immunity

### Resistances, Immunities & Movement
- **Automatic resistance/immunity resolution** from racial traits, subraces, feats, subclass passive features, subclass toggles, and attuned magic items
- **Immunity correctly supersedes resistance** to the same damage type
- **"Resistance to all damage" and "all except X" effects** expand into every individual damage type
- **Player-chosen resistance items** (Ring of Resistance, Armor of Resistance, Absorbing Tattoo, Orb of Shielding) get a real dropdown to pick which damage type your copy protects against, rather than guessing
- **Full movement tracking** — climbing, swimming, and flying speeds from racial traits and class features

### Magic Item Integration
- **836 magic items** with full descriptions
- **Attunement tracking** — max 3 attuned items (4 for Artificers at 10th level)
- **Automatic mechanical effects** for 252 items — resistances, immunities, ability score overrides, AC/save bonuses, and weapon damage bonuses, applied only while equipped/attuned
- **Searchable magic item browser** with filtering

### Gear & Inventory
- **Equipment browser** with search and category filtering, including a dedicated Materials category for browsable Silvered and Adamantine weapon variants
- **Quantity tracking** for stackable items
- **Equipment equipping** with computed AC and attack bonuses
- **Real tooltips on every item** — both in the reference browser and your actual owned inventory, showing weight, cost, and any real mechanical text (weapon properties, armor stats, special rules) rather than a blank or generic hover

### Feat Manager
- **138 feats** from all official sources
- **Feat prerequisites** — automatically checked
- **DM-granted feats browser** for feats gained outside normal class progression
- **Feat descriptions on hover**

### Interface & Customization
- **12 themes** — Obsidian, Dragon's Hoard, Shadowfell, Arcane Scroll (light mode), Feywild, Blood Moon, Frostspire, Cinderveil, Tavern Hearth, Mossgrove, Gearworks, Hallowed Stone
- **Resizable window** with draggable splitters between panels
- **Right-click any feature, race trait, or subrace trait** for a full detail popup
- **Search everywhere** — find spells, feats, items, and equipment instantly

### Save & Share
- **Save characters** to `~/.dnd_characters/`
- **Load characters** — pick up where you left off
- **Export and import** character files to share with others

### Dice Roller
- **Built-in dice roller** for any dice combination
- **Quick roll buttons** — d4, d6, d8, d10, d12, d20, d100
- **Advantage/Disadvantage** — roll twice, take the better/worse result
- **Modifier support and roll history**

---

## 🚀 Quick Start

**Requirements:** Python 3.9+ and pip.

```bash
pip install PySide6
python run_dnd_creator.py
```

A splash screen appears immediately and animates while the app loads in the background, so startup never looks frozen.

---

## 🛠️ Building a Standalone EXE

### Windows
```bat
build_exe.bat
```

### macOS / Linux
```bash
./build_exe.sh
```

**Output:** `dist/MIMIC.exe` (Windows) or `dist/MIMIC` (macOS/Linux). See [`BUILD_EXE.md`](BUILD_EXE.md) for the full guide.

---

## 🔧 Troubleshooting

### "No module named 'PySide6'"
```bash
pip install PySide6
```

### EXE starts but immediately closes
1. Run from a terminal/command prompt to see error output
2. Delete `build/` and `dist/` folders and rebuild
3. Check that `dnd_app/assets/` and `dnd_app/icon.ico` exist before building

### Splash screen looks frozen / doesn't animate
Make sure you're on current source — the heavy startup import now runs on a background thread specifically so the splash animation keeps playing while it loads.

---

## 📁 Project Structure

```
dnd_app/
  data/              # All game data (races, classes, spells, feats, items, etc.)
  core/              # Character model, calculator, builder, save/load
  ui/                # PySide6 widgets (main window, wizard, sheet, theme, etc.)
  assets/            # Splash screen image/GIF
  icon.ico           # App icon
run_dnd_creator.py     # Entry point
requirements.txt
DnD5eCharacterCreator.spec   # PyInstaller build spec
build_exe.bat / build_exe.sh # One-command build scripts
```

---

## 📚 Sources Covered

| Category | Sources |
|----------|---------|
| **Core Rules** | PHB (2014 & 2024), DMG |
| **Expansions** | XGE, TCE, SCAG, EEPC |
| **Settings** | ERLW, GGR, EGW, MOT, WBW, AAG, VRGtR, FTD, DLSotDQ, BPGotG, SCC, SCOC, AI, SAiS |
| **Adventures** | Curse of Strahd, Ghosts of Saltmarsh, Tomb of Annihilation, Baldur's Gate: Descent into Avernus |
| **Community Content** | One Grung Above (Grung), Locathah Rising (Locathah), The Tortle Package (Tortle) |
| **Unofficial** | Plane Shift: Amonkhet (Ambition/Solidarity/Strength/Zeal Domains), clearly marked as such in-app |

---

## 🙏 Credits

**Created by Ethan O'Brien**

**Built with:**
- Python — the language that made it possible
- PySide6 — the UI framework that brought it to life
- PyInstaller — for packaging it all into a single executable

**MIMIC is dedicated to every player who has ever said:**

> *"I wish I could build characters offline."*
> *"I wish I had all the options in one place."*

---

## 📄 License

MIMIC is free to use. It is not affiliated with or endorsed by Wizards of the Coast.

D&D 5e content is used under the Open Gaming License (OGL) and/or with permission from Wizards of the Coast.

---

## 🎯 What's Next

- [ ] 2024 ruleset — full support
- [ ] Hyperlinks — clickable spell/feat/ability references
- [ ] Broader auto-prepared spell coverage — remaining Cleric domains, Paladin oaths, Warlock patrons, Sorcerer/Druid subclasses
- [ ] Wider on-hit damage bonus coverage — more class features and magic items beyond the current set
- [ ] Player-choice magic item resistance for a few remaining items
- [ ] Magic items in Known Actions — wiring the 856-item catalog into the same real, usable-action system built for class features, race traits, and spells this pass
- [ ] Monster/bestiary integration (future)

---

**MIMIC** — *A treasure chest of 5e data.*
*Free. Offline. Hungry.*
