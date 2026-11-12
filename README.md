# Lawless - Tamrielic Distribution - OWL Patch

**Version 0.1.0**

Restores Tamrielic Distribution outfits on 14 Lawless NPCs when using the Open World Loot patch.

An ESL-flagged `.esp`: 14 record overrides, no new forms, no assets. Skyrim Special Edition and Anniversary Edition. Tested only on the Overhaul 1.2 load order.

## Requirements

- [Open World Loot - Encounter Zone and Loot Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/49681) (`Open World Loot.esp`)
- [Lawless - A Bandit Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/88080) (`Bandit War.esp`)
- Lawless - Tamrielic Distribution Patch Update (`Bandit War Expanded - Tamrielic Distribution.esp`)
- [Lawless - A Bandit Overhaul - Lawless Patch FOMOD](https://www.nexusmods.com/skyrimspecialedition/mods/88080) (`Bandit War Expanded OWL.esp`)

### Target versions

Built and checked against: Open World Loot - Encounter Zone and Loot Overhaul 2.8.0.0, Lawless - A Bandit Overhaul 2.1.0.0, Lawless - Tamrielic Distribution Patch Update 1.0.0.0, Lawless - A Bandit Overhaul - Lawless Patch FOMOD 2.1.0.0. `inputs.sha256` pins the exact plugins.

## The Problem

`Bandit War Expanded OWL.esp` does not master `Bandit War Expanded - Tamrielic Distribution.esp` and loads after it, so Dainty Sload and Haknir crews lose their regional outfits.

## What the Patch Does

Keeps the OWL record, including its weapon lists, and takes `DefaultOutfit` from the Tamrielic Distribution patch.


## Install

Install `dist/Lawless - Tamrielic Distribution - OWL Patch.esp` as its own MO2 mod, tick the plugin, and run LOOT. Its masters place it; no hand placement.

## Build from Source

See [BUILDING.md](BUILDING.md).

## Verification Status

- Checked: Spriggit round trip, and a separate parser for the ESL flag, masters, record count and no new forms.
- In game, 2026-11-07: loaded and booted with the full load order, 0 crash dumps. All records win on disk. One outfit read live before the split. Crews not inspected in game.

## Credits and Permissions

Holds no plugin data from other mods; `inputs/` is not tracked. Credit goes to the authors of the mods listed below.

Checked on 2026-11-11 and 2026-11-13 against each mod's Nexus permission block and author notes, not its description or readme. The plugin is derived from the mods below and stays under their authors' terms.

| Mod | Author | What the Nexus page says | Status |
|---|---|---|---|
| [Lawless - A Bandit Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/88080) | Ooreeoo | Free use with credit, and derived work must stay free use. | allowed |
| [Open World Loot - Encounter Zone and Loot Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/49681) | deletepch, Luridum and zinghunt | Upload, modification, conversion and asset use are allowed. | allowed |
| [Tamrielic Distribution](https://www.nexusmods.com/skyrimspecialedition/mods/71372) | TateTaylorOH (Tate Taylor) | Upload, modification and asset use are allowed with credit. Not in sold files. | allowed |

`Bandit War Expanded - Tamrielic Distribution.esp` comes from Lawless - Tamrielic Distribution Patch Update, kxgcayh's own patch built from Lawless and Tamrielic Distribution, so the two rows for those mods cover it.

Every source allows a patch like this with credit; credit the authors above when publishing. Lawless asks that derived work stay free use, so this patch must too.

## License

MIT, see [LICENSE](LICENSE).
