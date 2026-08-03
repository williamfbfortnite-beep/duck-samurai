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
| Waves end, level ends, you win | **A 100-level campaign** over one endless-feeling board — each level is a wave target you either hold or don't |
| A tower is a tower forever | **Merge.** Drop a duplicate on a unit to fuse it — Lv1 → Lv2 → Lv3 |
| Progress is a fixed level select | **Meta-loop.** Survival pays out points → crates → roster → multipliers |
| Sun that vanishes if you miss it | **Same rule, kept.** A Ki orb has to be clicked to bank it — left alone it drains away and is gone. Income is something you attend to, not something that accrues |

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

- **Ki (氣)** — in-run only, wiped at the end. Buys unit placements. Grown by Rice
  Paddies, and **only ever obtained by clicking**. An orb sits for nine seconds,
  blinks for the last three, then drains away with nothing banked. Nothing in the
  game credits Ki passively: the chain fusion that used to refund straight to the
  balance now sheds an orb like everything else, because one exception is all it
  takes for the clicking to become decorative. The cost of a big economy is now
  the attention it takes to harvest it.
- **Points (点)** — permanent. Earned by surviving. Buys crates and upgrades.

A save can be retired two ways. **切腹 START OVER** in the barracks wipes points,
stars, unlocks and campaign progress back to a fresh file; it takes two presses
because there is no undo, and the arming lapses after four seconds so a stray tap
cannot be confirmed later by an unrelated one. Separately, the storage key
carries a version — bumping it orphans older saves rather than deleting them, so
a payout change that would otherwise leave a player holding a roster the current
curve could never earn does not follow them forward.

---

## 2b. The campaign

100 levels in blocks of ten. Every level in a block shares a **wave target** —
levels 1-10 all ask you to hold to wave 10, 11-20 to wave 20, and so on until
91-100 ask for wave 100 — while difficulty climbs step by step *inside* each
block. Every fifth level fields an **elite**: an enormously inflated Oni on the
final wave, worth six times the points and impossible to ignore.

```
level    1 ─────── 10 │ 11 ─────── 20 │ … │ 91 ────── 100
target       wave 10  │    wave 20     │   │   wave 100
elite         5, 10   │    15, 20      │   │    95, 100
```

### Valor (武功) — why wave 100 is possible at all

Towers cap out at Lv3 × 5★. Without something else, the player's ceiling is
fixed while the tide keeps climbing, and wave 100 is arithmetically unwinnable.
So **every wave you clear permanently strengthens the whole line for the rest of
the run** — +5% damage, +4% HP, compounding to about ×6 by wave 100. Surviving
is itself the scaling mechanic.

The enemy curve was flattened to match. It used to be `1.115^(w-1)`, which
reaches **47,886×** by wave 100; it is now linear-plus-gentle-quadratic, topping
out near **25×**. Measured end to end by fast-forwarding real runs:

| Board | Outcome at level 91 (target wave 100) |
| --- | --- |
| Lv3 fusions, 5★, all upgrades | **reached wave 100**, 3-15 zombies alive |
| Plain Lv2 units, no fusions | **died at wave 74**, 130 zombies piled up |

Reachable, but only with real investment.

---

## 3. The board

Five lanes × eight columns. Zombies enter from the east (right), walk west, and
eat anything in the way. Past column 0 sits each lane's **Ofuda Ward** — a paper
talisman that immolates one lane, one time. Second breach in a lane is the end of
the run.

```
 ┌───┬───────┬───────────────────────────┬──────────────┐
 │ 御 │       │ ·  ·  ·  ·  ·  ·  ·  ·    │              │  ← lane 1  ward intact
 │ 札 │ bank  │ ·  ·  ·  ·  ·  ·  ·  ·    │  bonsai      │  ← lane 2
 │   │ stones│ ·  ·  ·  ·  ·  ·  ·  ·    │  border      │  ← lane 3   zombies
 │ W │ shrubs│ ·  ·  ·  ·  ·  ·  ·  ·    │              │  ← lane 4    enter →
 │ A │       │ ·  ·  ·  ·  ·  ·  ·  ·    │              │  ← lane 5
 └───┴───────┴───────────────────────────┴──────────────┘
 x184  approach  x276   8 columns × 94px   x1028    x1264 muster
   ↑ ward + loss line     one per painted square
```

**The map draws its own grid, and the code uses it.** Each lane is painted as a
checkerboard of alternating grass squares, and *that* is the grid a player reads.
A duck centred in a code tile that does not line up with the paint stands half in
one square and half in the next however perfectly centred it is on its own tile —
which is exactly what it looked like. Measured out of the art, the seams run at a
pitch of **93.83px with the first at x 182**: ten squares across the board.

The westmost sits on the boulders and the eastmost inside the bonsai border, so
eight are on open ground — **x 276..1028, at 94px steps, tracking the painted
seams to within 1.4px across the whole width.** That is why the board is eight
columns and not nine: nine cannot be aligned to this map at *any* offset, because
the painted pitch does not divide that way. The decoration becomes the border it
was drawn as, and every duck stands in the middle of a square.

This also fixed the older problem it was masking. A grid spanning the full width
had put eleven of the 45 tiles on top of scenery, so a duck placed at the west end
of lane 3 stood in the branches of a potted tree.

Two things had to move with it, and both are difficulty levers disguised as
geometry.

The **ward** burns a lane when something reaches it, and that trigger was written
as `GX - 26` — correct only by coincidence, while the field happened to start at
124. Left alone it would have put the burn line two hundred pixels east of the
paper doing the burning. Both now derive from `WARD_X`.

The **muster point** is the subtle one. What sets difficulty is not the length of
the lane but how long a zombie spends being shot at, and that is the sum, over
every tower, of the distance it covers while east of that tower. Pulling the grid
inside the garden moved the back rank 161px east and that sum fell 12%. The
campaign ceiling survived — a fully invested board still cleared wave 100 — but a
mid-strength board that used to reach wave 72 died at 65, a difficulty change
nobody asked for, arriving as a side effect of a cosmetic fix. Moving the muster
the muster east puts the sum back to 99.9%, and the ward moves east to match so
the total run stays 1064px, exactly as before the grid ever moved.

Re-simulated end to end after the realignment, on the same five-column reference
layout throughout — 72 originally, 65 once the grid moved, **74 now**, with an
invested board still clearing wave 100. Restored, inside the noise.

The lesson worth keeping: *total lane length is not the difficulty knob.* Two
boards can have identical spawn-to-ward distance and differ by 12% in damage
taken, purely from where the towers sit inside it.

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

The barracks roster and the crate pool are the **same list** — `CRATE_POOL`, the
units minus the fusions. They used to be built separately, so the roster listed
all twelve fusion results as locked cards reading *"find it in a crate"*, a
promise the game cannot keep: a fusion exists only by fusing two units on the
board. Fusions belong to the codex, where they are discovered rather than bought.
They also cost 0 氣 — deliberately, since you pay with the two units consumed —
so one reaching the tray would be an unlimited free tier-2 unit. A save claiming
to own a fusion is scrubbed on load, and the tray is filtered again at run start.

### Fusion — the other half of the mechanic

Dropping a **different** unit onto one already on the board fuses them, if the pair
has a recipe. The result is a unit that exists nowhere else — not in crates, not in
the tray — and it **inherits the level of the unit already on the tile**, so fusing
onto a Lv3 hands you a Lv3.

| | + | | → | Fusion |
| --- | --- | --- | --- | --- |
| 苦無 Kunai Duck | + | 氷 Frost Lantern | → | **氷刃 Frostblade Duck** — twin frozen blades, 50% slow |
| 扇 Twin Fan | + | 雷 Thunder Drum | → | **雷扇 Storm Fan** — chains 4 targets across three lanes |
| 竹 Bamboo Wall | + | 長刀 Naginata Ronin | → | **鉄壁 Iron Bulwark** — 900 HP that swings back |
| 弓 Yumi Sniper | + | 爆 Powder Keg | → | **爆矢 Bombardier** — piercing arrows that detonate |
| 稲 Rice Paddy | + | 狐 Fox Shrine | → | **豊穣 Harvest Spirit** — Ki income *and* an aura |
| 氷 Frost Lantern | + | 爆 Powder Keg | → | **氷爆 Frost Mine** — a wide bloom of ice |
| 苦無 Kunai Duck | + | 稲 Rice Paddy | → | **暁 Dawn Herald** — a shooter that pays its own way |
| 竹 Bamboo Wall | + | 爆 Powder Keg | → | **茨 Thorn Wall** — hurts whatever chews on it |
| 扇 Twin Fan | + | 弓 Yumi Sniper | → | **疾風 Wind Herald** — three piercing blades, fastest on the board |
| 雷 Thunder Drum | + | 狐 Fox Shrine | → | **鎮魂 Grave Bell** — chains, and refunds Ki as it kills |
| 苦無 Kunai Duck | + | 長刀 Naginata Ronin | → | **炎僧 Ember Monk** — a burning sweep that keeps burning |
| **鉄壁 Iron Bulwark** | + | 氷 Frost Lantern | → | **潮守 Tide Warden** — *tier 2*: 1200 HP and an aura of mud |

Eleven recipes take two buildable units. The twelfth is **tier 2**: its left-hand
ingredient is itself a fusion, so you build a Bulwark on the board first and then
drop a Frost Lantern card onto *that*. Same interaction, one layer deeper.

Two rules keep fusions special. **One of each species may stand on the field at a
time** — a second Frostblade is refused, so a board is a spread of different
fusions rather than five copies of the best one. And every recipe is **sealed
behind a campaign level** (3, 6, 9, 13, 18, 24, 31, 39, 48, 58, 69, and 80 for
the tier 2), so the roster opens across the whole 100 levels.

The **Fusion Codex** on the menu tracks all twelve, and deliberately tells you
almost nothing. Until you have actually made a fusion it hides **both ingredients
and the result** — the codex only distinguishes *sealed* (locked by level) from
*unsealed — go find it*. Discovery happens on the board: hovering a pair that
works names the result before you commit, so experimenting is safe but the
combination itself is yours to find.

### Every unit says what it does

Role, description and stat chips are generated from the same fields the simulation
reads — damage, rate, HP, reach, slow, burn, thorns, blast radius — so a card can
never advertise behaviour a unit does not have. They appear on the barracks cards,
in the codex for discovered fusions, and on a hover panel over the in-run tray.

---

## 5. Roster — the flock

| Unit | 漢字 | Ki | Rarity | Role |
| --- | --- | --- | --- | --- |
| Rice Paddy | 稲 | 50 | Common | Economy — a Ki orb every 8s; merging is sub-linear on purpose |
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

Payout is **per level cleared**, not per second survived:

```
clear a level :  (40 + 10 × level) × (1 + CoinMultiplier)
fail a level  :  30% of that, scaled by how far you got
```

The old formula paid by score, so a single deep run handed over 30-40,000 points
— most of the campaign's entire economy in one sitting. Clearing all 100 levels
once now pays **54,500** total, against roughly 64,000 of upgrades plus crates,
so the meta is a campaign-length arc rather than an afternoon.

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

**Every duck bobs along to the soundtrack** — head thrust *forward* on the beat
and drawn back after, the way a chicken walks, not a vertical nod. Sprites draw
in two slices, head and neck as rows 0-8 and body from row 9; the cut can be
clean because a horizontal thrust needs no overlap to hide a seam, the neck
simply riding over the wider body top.

The offset is applied *inside* the mirrored transform, so one positive number
means "toward the bill" for everyone: defenders facing right thrust right,
zombies facing left thrust left. Verified in isolation on a blank canvas — a
thrust of 10 moves the defender's head exactly +10px and the zombie's exactly
-10px.

**The thrust is quantised, never interpolated.** Pixel art that slides by
fractions of a pixel reads as a blurry modern sprite, so the head snaps between
whole *sprite* pixels — 0 → 1 → 0 across the beat, two discrete states rather
than a glide. One pixel of travel is deliberate: two reads as a duck
headbanging rather than a duck keeping time.

Making that true meant fixing the base scale. `SCL` was 1.12, which put one
sprite pixel at 4.48 screen pixels, so nothing in the game ever landed on a
clean grid and the head stepped unevenly — 4px, then 5px. It is now **1.25**, an
exact 5 screen pixels per sprite pixel, and every scale a caller passes is
snapped to quarter steps so pops, bosses and elites stay integral too. The body
bobs were sliding by single *device* pixels — a fifth of a sprite pixel, far too
small to read — and are now whole sprite pixels as well.

The tempo was measured off the track itself (148.25 BPM, first beat at 0.03s)
and it runs at half-time, which reads as a groove rather than a twitch. It is
driven by the audio element's own playhead, so it stays in time however long the
loop has been running, and falls back to the game clock when the music is off.
The defenders bob on the beat; the dead bob half a beat late.

The bob is **purely horizontal** for anything standing still. A planted duck used
to also hop one sprite pixel every couple of seconds, which at this scale is four
screen pixels — big enough to read as a twitch rather than a breath, and it
fought the head thrust already carrying the idle. Only a duck that is walking
moves vertically now, because there the bob *is* the step.

**Objects** are a second, free-size layer over the same idea: each has its own
grid and palette. Twenty of them cover the projectiles (shuriken, war fan, ice
shard, arrow, bile), the Ki orb, the Ofuda ward, a 3-frame explosion, the three
supply crates, the shovel icon, and the props that dress the board — lily pads,
rocks, duck skulls, reed clumps, stone lanterns, and the shrine gates on the
horizon. Props are placed from a fixed seed so the field never reshuffles between
runs.

Palette inherits the existing Duck Samurai page: `#0d0716` night, `#f0c987` gold,
rot-green `#8fae6a` for the tide. Same dusk, later in the evening, much worse.

**The sky moves.** A run opens at sunset and runs a full day/night cycle every 165
seconds — the ground is cached once, the sky is redrawn each frame from an
interpolated palette, the sun and moon ride the same arc half a cycle apart, stars
fade in, and the whole field is washed in the light of whatever hour it is.

**The battlefield is painted, not generated.** A hand-drawn 1122×765 pixel map
(`assets/map.png`) is the ground now, drawn 1:1 with no resampling — the canvas
was resized to the art rather than the art squeezed into the canvas — and the
day/night cycle tints it rather than rebuilding it. The procedural tile field it
replaced is gone.

Because the map is drawn at a slight angle, its lanes are not uniform: they run
65px at the top and 113px at the bottom. The bands were measured out of the
pixels and live in a hand-written `LANES` table instead of a computed grid.

Those bands describe where the **grass** is, which is not the same as where you
can **click**. The kerbs between them are drawn stone, and treating them as
non-lane left about 15% of the board as dead space. `LANE_EDGE` cuts the hit
boundaries midway between neighbouring bands, so the field is covered edge to
edge and every pointer position belongs to exactly one lane. The hover highlight
draws the hitbox, not the grass band: what you see is what you click. Effects
that describe the walkable strip — frost, splash outlines — still use the grass
bands, because that is where things actually stand.

**1122×765 is a coordinate space, not a resolution.** Every coordinate in the
code is expressed in it, but the buffer the game actually draws into is sized to
the display and the context scaled to match, so nothing in the game code had to
change. Without that, a screen larger than the art gets pixels the game never
drew — the board goes soft while the DOM chrome around it stays sharp, which is
exactly what "it looks low resolution" describes.

Pixel art also wants one art pixel to cover a *whole* number of screen pixels.
At 1.18 the edges alternate one and two pixels wide and the art turns to mush,
so the board is trimmed to a width where the ratio comes out whole — worth up to
a fifth of the width, and past that filling the space wins instead. On a 1× panel
that means the board sits at 1122px with 1:1 pixels; on a 2× panel it sits at the
same size with a 2244×1530 buffer, so every art pixel is exactly four screen
pixels. The surface is capped at twice the art, because the map holds 1122px of
real detail and the sprites are stamped from 16×18 grids — beyond 2× there is
nothing further to resolve, only a bigger buffer to blit sixty times a second.

Paying for that resolution meant giving some back. The field is baked once per
tint step rather than recomposited per frame — the day is 165 seconds long, so
240 steps is a rebuild every 0.7s and no eye reads it as banding — and the
`clearRect` that used to precede it is gone, since the field is opaque and
covers the whole surface, making the clear a second full-surface pass for
nothing. Together those hold 60fps on a 2× board through a typical wave.

**One number caused three separate bug reports.** When the board was refitted to
the map, `VW/VH` became 1122×765 but the `<canvas>` element kept its old 16:9
attributes of 1152×648, and nothing enforced the pair. That single stale value
produced:

- the map losing its bottom 117px, and showing 30px of bare canvas down the
  right-hand edge — precisely the strip the tide walks in through;
- sprites in the last lane sliced off at the knees, because their feet sat at
  y 674 on a surface that stopped at 648;
- and the cursor selecting the lane *below* the one under it, because the
  surface was being stretched to fill a 1122×765 frame while `toBoard` divided
  by 765 — an 18% mismatch, which is almost exactly one lane at the centre of
  the board.

The lesson is in the third one. A hover test that converts canvas coordinates to
screen coordinates *using the same maths the game uses*, and then checks the game
agrees, will pass no matter how wrong that maths is — it validates a function
against its own inverse. The test that caught this reads the rendered pixels: it
finds where something actually got drawn and puts the cursor there. The canvas
size is now set in script from `VW`/`VH`, so the two cannot drift again.

## 9. Audio

The soundtrack is **an original recording by the player** — a 2:38 track,
looped, replacing the synthesized score that used to sit here. It plays through
a plain `<audio>` element rather than the WebAudio graph on purpose: media
playback is the one path iOS keeps in the "playback" audio session, so the music
survives the ringer switch even where a bare AudioContext would not.

Sound effects are still synthesized at runtime — throwing, impacts, biting,
deaths, the ward, crates, the boss walking on, and fusion — so the only asset in
the project is the music itself. It lives at `assets/music.mp3` and is referenced
relatively; the artifact build inlines it as a data URI, since a published page
is a single self-contained file whose CSP blocks every external host.

Everything mixes through one master bus, which is also how the output gets
verified: an analyser taps the bus and measures true peak and RMS, so "is this
audible" is a number rather than an opinion. Target is a peak around 0.5.

Audio never blocks play. If a host refuses an AudioContext the game notices once
and runs silently, and the speaker icon tells the truth — 🔊 playing, 🔈 blocked
until you click, 🚫 refused outright — instead of always claiming sound is on.

**iOS needs its own output path.** A bare AudioContext on iPhone runs in the
*ambient* audio session, which the ringer/silent switch mutes — so the game plays
in total silence with a perfectly healthy audio graph and no error anywhere. The
master bus is therefore piped through a MediaStream into an `<audio>` element on
iOS, which moves output into the *playback* session and ignores that switch. It
can be toggled in Sound Check if a device dislikes the routing.

**Sound Check** (on the menu) exists because no automated test can confirm a
speaker actually made noise. It shows the engine state, the sample rate, a live
output meter tapped off the master bus, and a loud test chime. A moving bar with
no sound means the problem is downstream — tab muted, wrong output device, or an
iPhone ringer switch, which silences web audio. A flat bar means the page itself
is being denied audio. The first gesture also plays a silent clip to nudge iOS
out of that ringer-switch audio session.

---

## 10. Build status

**Shipped in `game.html`** (single file, no dependencies, opens from disk):
board, merging, fusion + codex, 10 buildable units and 6 fusion results, all 6
enemies, endless waves, wards, Ki economy, score → points, crates with reveal
animation, all four upgrade tracks, loadout picker, day/night cycle, tiled lanes,
music and SFX, localStorage save, pause and 2× speed.

**Next, in rough priority order:** a "sell for 50%" shovel refund curve that scales
with level; lane hazards (mud that slows your own melee, a bridge column that can
be cut); a Kappa Digger that tunnels the first two columns to punish back-loading;
daily seeds with a shared leaderboard string.
