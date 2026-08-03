# Map generation prompts — 鴨侍 Duck Samurai

Ten themed battlefields. Paste one prompt per generation.

---

## Read this first — the technical part matters more than the theme

The first map we integrated was beautiful and still cost an afternoon, because
of things the prompt didn't ask for. Every prompt below carries a **SPEC** block
that fixes them. Don't drop it.

What went wrong last time, and why each rule exists:

| Rule | Why |
| --- | --- |
| **Flat top-down, no perspective** | The first map was drawn at a slight angle, so its lanes ran 66px at the top and 114px at the bottom. Uniform grid code couldn't fit it — it needed a hand-measured lane table. Equal lanes make a map drop straight in. |
| **Exactly 1122 × 765** | Matches the canvas 1:1, so the art draws with no resampling. Any other size gets scaled and the pixels blur. |
| **5 lanes, equal height, full width** | The engine is five lanes across eight columns. |
| **If you paint a grid, paint the right one** | The second thing that cost real work. The first map drew each lane as a checkerboard of alternating grass squares — a lovely touch, and a grid the player reads as the tiles. It came out at a 93.83px pitch, which the engine's columns did not match, so every unit stood half in one square and half in the next. The board had to be rebuilt around the paint: eight columns of 94px from x 276. **Either paint no squares at all, or paint exactly 8 across x 276..1028 — 94px each.** Anything else and the code has to follow the art again. |
| **Leave the left 276px as a bank** | The nests and ofuda wards live there — the ward burns at x 200. Lane content must not start until x 276. |
| **Keep x 276–1028 clear of standing objects** | This is the one that cost the most. The first map was decorated right across the lawn — potted bonsai, shrubs, boulders — and a full-width grid put eleven of its tiles on top of scenery, so a duck placed there stood in the branches of a tree. The grid had to be pulled inside the decoration to find clean ground. **Decoration belongs outside that window, or flat inside it.** Flat is fine — gravel, stone paving, moss, fallen leaves, a patch of different grass. What breaks it is anything with height: pots, bushes, rocks, lanterns, posts. |
| **Keep the top 90px calm** | The HUD sits there. Busy art makes the numbers unreadable. |
| **Keep the bottom 85px calm** | The card tray sits there. |
| **Hard pixel edges, no anti-aliasing, no gradients, limited palette** | It's pixel art or it isn't. |
| **Export PNG** | The first map came inside a PDF as a JPEG — 95,926 distinct colours where pixel art uses dozens. It works, but the palette is permanently smeared. **PNG, never JPEG, never inside a PDF.** |

Ideal lane bands for a 1122×765 canvas, if the model will respect numbers:

```
   0 –  90   header    (calm, HUD)
  90 – 208   lane 1  ┐
 208 – 326   lane 2  │
 326 – 444   lane 3  ├ 118px each, full width, divided by a clear border
 444 – 562   lane 4  │
 562 – 680   lane 5  ┘
 680 – 765   footer    (calm, card tray)
     x < 276           west bank — nests and wards, no lane content
```

---

## The SPEC block — append to every prompt below

> **SPEC —** Pixel art, exactly 1122×765 pixels. Strict flat top-down view, like
> a SNES tactics map: **no perspective, no isometric skew, no vanishing point.**
> Five horizontal lanes of **identical height**, running the full width, each
> separated by a clearly readable border (stone kerb, low hedge, plank edging or
> water channel). If the lanes are subdivided into squares, there must be
> **exactly 8 of them per lane, 94px wide, running x 276 to x 1028** — units are
> centred on those squares, so any other spacing leaves them straddling seams.
> No subdivision at all is equally fine. **Between x 276 and x 1028 the lanes
> must be flat and free of any standing object** — no pots, bushes, rocks, lanterns, posts or statues;
> units are placed there and anything with height ends up with a duck standing
> in it. Flat detail inside that window is welcome and wanted: gravel, paving,
> moss, fallen leaves, patches of different grass. Put every three-dimensional
> prop in the margins — left of x 276 and right of x 1028 — where it reads as a
> border. Reserve the leftmost ~276px as a distinct bank or threshold with no
> lane content. Keep the top ~90px and bottom ~85px visually calm and
> low-contrast.
> Hard pixel edges, no anti-aliasing, no gradients, no blur, no drop shadows,
> limited palette of roughly 32–48 colours, visible consistent pixel grid.
> Japanese setting, no text or lettering anywhere in the image. Export as PNG.

---

## 1. 竹林 — Bamboo Grove

A dense green bamboo grove cut through by five raked earth paths. Towering
bamboo stalks crowd both margins, pale green and gold, throwing thin vertical
shadows. Lane borders are low bamboo fencing lashed with dark rope. Scattered
fallen leaves, a mossy stone water basin on the west bank, a stone lantern half
swallowed by growth. Cool filtered daylight, deep greens and warm straw yellows.

## 2. 蓮池 — Lotus Pond

A temple water garden. Five wooden boardwalks run west to east over still dark
water, lily pads and pink lotus blooms crowding between them. Koi shapes drift
under the surface. Lane borders are weathered plank edging with rope rails.
Reeds and iris at the margins, a half-sunken torii at the western bank. Teal
water, warm cedar planks, pink and jade accents.

## 3. 雪社 — Winter Shrine

Deep snow over a shrine approach. Five swept stone paths, snow banked in ridges
between them. Bare black plum branches with a few red blossoms, frozen stone
lanterns wearing snow caps, a rope-and-paper shimenawa strung along the north
edge. Footprints and drifts. Near-white with blue shadow, black timber, single
vermilion accents.

## 4. 紅葉 — Autumn Maple Temple

A temple courtyard under full autumn colour. Five gravel walks separated by low
moss kerbs, drifted thick with scarlet and orange maple leaves. Old maples at
the margins, their canopies intruding at the top edge. A moss-furred stone
buddha on the west bank, a bamboo deer-scarer over a trickle of water. Crimson,
burnt orange, deep moss green, grey gravel.

## 5. 腐蘆 — The Rotting Reeds

*The battlefield the game is named for.* A drowned marsh gone bad. Five raised
mud causeways over stagnant green-black water, thick with dead and rotting
reeds. Sickly yellow-green scum, bubbles, half-sunken bones and broken shrine
posts. Drifting mist in the low ground. Lane borders are collapsing timber
revetments. Rot green, bile yellow, drowned brown, cold grey mist. Ominous but
still readable.

## 6. 城砦 — Castle Courtyard

The outer bailey of a mountain castle. Five flagstone avenues divided by dressed
stone kerbs. Massive fitted-stone rampart walls along the top and bottom edges,
arrow slits and white plaster. Racks of spears, straw training dummies, a
war-drum on a stand at the west end. Grey granite, white plaster, black timber,
deep indigo banners.

## 7. 漁村 — Fishing Village

A harbour at low tide. Five weathered jetties running out over wet sand and
tidal pools. Nets on drying frames, crab traps, coils of rope, upturned skiffs
at the margins. Barnacled pilings, seaweed, gulls. The western end rises to a
stone quay. Driftwood grey, wet sand ochre, rope tan, cold sea green.

## 8. 火山 — Volcanic Onsen

A hot spring terrace on volcanic rock. Five pale mineral-crust walkways between
steaming pools of milky turquoise water. Black basalt, sulphur-yellow crusting,
drifting steam. Bamboo pipes feeding the pools, a red-lacquered rail along the
north edge. Black rock, milky blue, sulphur yellow, ember orange in the cracks.

## 9. 墓地 — Night Graveyard

A hillside burial ground under a full moon. Five gravel paths between rows of
weathered stone grave markers and toppled slabs. Ghost-lanterns floating, thin
ground mist, gnarled dead trees at the margins. A moss-covered ossuary at the
west end. Blue-black night, bone grey, sickly green witch-light, cold white
moonlight. Dark but the lanes must stay clearly readable.

## 10. 稲田 — Rice Terraces at Harvest

Flooded rice terraces at golden hour. Five earth dykes running between paddies
of ripe rice, heavy gold heads bowing, still water mirroring the sky below them.
Straw bundles stacked at the margins, a wooden water wheel, scarecrows on
bamboo poles. Warm gold, wet green, sunset orange on the water, dark earth
dykes.

---

## When the images come back

Send them as **PNG attachments** and I'll do the rest. The pipeline already
exists from the first map: measure the lane bands out of the pixels, fit the
grid, drop them in. Two things I'd want to add once there's more than one:

- **Per-level maps** — the campaign rotates battlefield every ten levels, so the
  block you're on is visible at a glance.
- **A map picker** in the barracks for replaying a cleared level anywhere.
