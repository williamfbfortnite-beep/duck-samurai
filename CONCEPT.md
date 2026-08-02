# 鴨侍 — SIEGE OF THE ROTTING REEDS
### A lane-defence game about duck samurai, merging, and an undead tide that never stops

---

## 1. The pitch

The moon over the rice paddies has gone the colour of old bone. Something in the
water has turned the flock — feral, rotting, and marching west toward the shrine
gate. You are the last retainer. You have coin, conscripts, and until dawn.

**Plants vs. Zombies' skeleton, with three bones replaced.**

| PvZ does this | We do this instead |
| --- | --- |
| Waves end, level ends, you win | **Endless.** There is no win screen, only how long you lasted |
| A tower is a tower forever | **Merge.** Drop a duplicate on a unit to fuse it — Lv1 → Lv2 → Lv3 |
| Progress is a fixed level select | **Meta-loop.** Survival pays out points → crates → roster → multipliers |
| One-shot resource clicking | Ki orbs auto-collect after a beat, so the game is about placement, not clicking |

The fantasy: *your line gets stronger inside a run (merging) and across runs
(crates + upgrades), so a wave that ended you an hour ago is now Tuesday.*

---

## 2. Core loop

```
        ┌──────────────────────────────────────────┐
        │  RUN: survive waves → earn Score         │
        │    · spend Ki → place units              │
        │    · place a duplicate → MERGE, power up │
        │    · a breach past the wards → run ends  │
        └───────────────┬──────────────────────────┘
                        │  Score × (1 + Coin Multiplier)
                        ▼
        ┌──────────────────────────────────────────┐
        │  BARRACKS: spend points                  │
        │    · crates → unlock units / ★ dupes     │
        │    · upgrades → multiplier, Ki, wards    │
        └───────────────┬──────────────────────────┘
                        │  stronger roster + better payout
                        └──────────► back into the run
```

Two currencies, deliberately not interchangeable:

- **Ki (氣)** — in-run only, wiped at the end. Buys unit placements. Grown by Rice Paddies.
- **Points (点)** — permanent. Earned by surviving. Buys crates and upgrades.

---

## 3. The board

Five lanes × nine columns. Zombies enter from the east (right), walk west, and
eat anything in the way. Past column 0 sits each lane's **Ofuda Ward** — a paper
talisman that immolates one lane, one time. Second breach in a lane is the end of
the run.

```
 ┌───┬───────────────────────────────────────────────────┐
 │ 御 │ · · · · · · · · ·                                 │  ← lane 1  ward intact
 │ 札 │ · · · · · · · · ·                                 │  ← lane 2
 │   │ · · · · · · · · ·                                 │  ← lane 3   zombies
 │ W │ · · · · · · · · ·                                 │  ← lane 4    enter →
 │ A │ · · · · · · · · ·                                 │  ← lane 5
 └───┴───────────────────────────────────────────────────┘
   ↑ wards            9 buildable columns              ↑ spawn
```

---

## 4. The twist: merging

Selecting a card and clicking a tile that **already holds the same unit at the
same level** fuses them. You pay the card's cost again; you get one unit a tier
stronger, occupying one tile.

| Level | Damage / HP | Fire rate | Look |
| --- | --- | --- | --- |
| ★ Lv1 | ×1.0 | ×1.0 | plain |
| ★★ Lv2 | ×1.85 | ×1.12 | gold trim, 2 pips |
| ★★★ Lv3 | ×3.30 | ×1.28 | gold aura, 3 pips |

Why it matters: board space is the real scarce resource, not Ki. A Lv3 Kunai Duck
out-damages three Lv1s *and* leaves two tiles free. But merging concentrates your
line — one well-placed Ronin eats a Lv3 and you've lost three units' worth of Ki
at once. Spread wide and survive chip damage, or stack tall and pray.

Dupes pulled from crates feed a second axis: each duplicate adds a permanent
**★ star** to that unit (+6% damage and HP each, max 5), so crates never dead-end.

---

## 5. Roster — the flock

| Unit | 漢字 | Ki | Rarity | Role |
| --- | --- | --- | --- | --- |
| Rice Paddy | 稲 | 50 | Common | Economy — grows a Ki orb every ~6.5s |
| Kunai Duck | 苦無 | 100 | Common | Baseline lane shooter |
| Bamboo Wall | 竹 | 50 | Common | 400 HP of nothing-personal |
| Twin Fan | 扇 | 175 | Uncommon | Two blades a volley, fast |
| Frost Lantern | 氷 | 150 | Uncommon | Chip damage + 45% slow |
| Powder Keg | 爆 | 125 | Uncommon | Proximity mine, 1.6-tile blast, consumed |
| Naginata Ronin | 長刀 | 200 | Rare | Melee sweep, hits everything in reach |
| Yumi Sniper | 弓 | 300 | Rare | Pierces the entire lane |
| Thunder Drum | 雷 | 325 | Epic | Chains to 3 targets across neighbouring lanes |
| Fox Shrine | 狐 | 250 | Epic | Aura: +25% fire rate to the 8 tiles around it |

Six go into a loadout. You start with the three Commons.

## 6. Roster — the tide

| Enemy | HP | Speed | From wave | Gimmick |
| --- | --- | --- | --- | --- |
| Rot Duckling | 110 | slow | 1 | The wave filler |
| Feral Sprinter | 75 | fast | 3 | Punishes an unfinished lane |
| Armoured Ashigaru | 270 | slow | 5 | 35% damage reduction until the helm cracks at half HP |
| Bile Spitter | 130 | slow | 7 | Outranges melee, spits from 3 tiles |
| Undead Ronin | 360 | medium | 9 | Hits like a truck, kills a Lv1 in two swings |
| **Oni Hulk** | 1500 | crawl | every 10th | Boss. Ignores knock, eats walls whole |

Scaling is exponential-but-gentle: `HP × 1.115^(wave-1)`. Wave 20 hulks are eight
times the wave-1 statline, which is what forces merging rather than sprawling.

---

## 7. Payout maths

```
Score  +=  (1.5 + wave × 0.75) per second survived   +   kill value per corpse
Points  =  floor( Score × (1 + CoinMultiplier) )
```

Surviving deeper pays *super-linearly* — the per-second rate itself scales with
wave — so the incentive is always "one more wave", never "farm wave 3 forever".

### Coin Multiplier — the requested ladder

Eight tiers, 5% → 40%, each strictly pricier than the last:

| Tier | Bonus | Cost |
| --- | --- | --- |
| I | +5% | 300 |
| II | +10% | 750 |
| III | +15% | 1,500 |
| IV | +20% | 2,600 |
| V | +25% | 4,200 |
| VI | +30% | 6,400 |
| VII | +35% | 9,500 |
| VIII | +40% | 14,000 |

Total to max: **39,250 points.** Three more escalating tracks sit beside it —
Ki Reserve (starting Ki), Ward Blessing (a second talisman per lane), and Crate
Fortune (rarity odds).

### Crates

| Crate | Cost | Pulls | Common / Uncommon / Rare / Epic |
| --- | --- | --- | --- |
| Ash | 400 | 1 | 70 / 23 / 6 / 1 |
| Iron | 1,100 | 3 | 45 / 35 / 16 / 4 |
| Gold | 3,000 | 5 | 15 / 35 / 35 / 15 — one Rare+ guaranteed |

Duplicates become stars, so a Gold crate is never a dud. Pull a unit already at
5★ and it refunds instead (100 points, +140 per rarity step), so the tail end of
the roster still pays into the upgrade tracks.

---

## 8. Art direction

Hand-authored pixel art, nearest-neighbour upscaled ×4. Nothing on screen is a
canvas primitive.

**Characters** are 16×18 grids built from one shared duck silhouette plus stamped
accessory layers (helmets, masks, weapons, lanterns, rags) and per-skin palette
swaps — so a new unit costs a colour table and two small overlays, not a new
sprite. Every character animates on a **3-frame cycle** — stand, stride-out,
stride-through — with a 1px body bob, and units *march onto their tile* when
placed, so the walk cycle is used by both sides.

**Objects** are a second, free-size layer over the same idea: each has its own
grid and palette. Twenty of them cover the projectiles (shuriken, war fan, ice
shard, arrow, bile), the Ki orb, the Ofuda ward, a 3-frame explosion, the three
supply crates, the shovel icon, and the props that dress the board — lily pads,
rocks, duck skulls, reed clumps, stone lanterns, and the shrine gates on the
horizon. Props are placed from a fixed seed so the field never reshuffles between
runs.

Palette inherits the existing Duck Samurai page: `#0d0716` night, `#f0c987` gold,
rot-green `#8fae6a` for the tide. Same dusk, later in the evening, much worse.

---

## 9. Build status

**Shipped in `game.html`** (single file, no dependencies, opens from disk):
board, merging, all 10 units, all 6 enemies, endless waves, wards, Ki economy,
score → points, crates with reveal animation, all four upgrade tracks, loadout
picker, localStorage save, synthesized audio, pause and 2× speed.

**Next, in rough priority order:** a "sell for 50%" shovel refund curve that scales
with level; lane hazards (mud that slows your own melee, a bridge column that can
be cut); a Kappa Digger that tunnels the first two columns to punish back-loading;
daily seeds with a shared leaderboard string.
