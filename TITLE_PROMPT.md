# Title screen prompt — 鴨侍 Duck Samurai

One illustration, used as the backdrop behind the menu. Paste the whole thing,
SPEC block included.

---

## Read this first — where the UI actually sits

The menu is real DOM drawn *on top* of this image, so the picture has to leave
room for it. Measured off the running game on a 1140×768 canvas:

```
 ┌───────────────────────┬──────────────────────────────────────┐
 │                       │                                      │
 │   FOCAL THIRD         │   MENU PANEL — x 266..1070           │
 │   x 0..380            │   y 159..609                         │
 │   the hero, the       │   title, level, four buttons         │
 │   silhouette, the     │   sits under a dark scrim that       │
 │   thing you look at   │   deepens left → right               │
 │                       │                                      │
 └───────────────────────┴──────────────────────────────────────┘
   keep it readable        keep it QUIET — low contrast, no
   and high contrast       busy detail, nothing you'd miss
```

The game already darkens the right side heavily (about 30% opacity at the left
edge rising to 94% at the right). So detail over there is *thrown away* — put
your effort in the left third and let the right fall into shadow.

**Do not draw the logo.** 鴨侍, the subtitle and every button are rendered by the
game in its own font. Any lettering in the image collides with them.

---

## The SPEC block — keep it attached

> **SPEC —** Pixel art, exactly **1140 × 768** pixels. Hard pixel edges, no
> anti-aliasing, no gradients, no blur, no drop shadows. Limited palette of
> roughly 32–48 colours with a visible, consistent pixel grid — the pixels must
> be square, uniform, and the same size across the whole image. Painterly
> shading, soft light or smooth blending are all wrong; this must read as
> hand-placed pixels.
>
> **Composition:** the subject sits in the **left third** of the frame and is
> the highest-contrast thing in the picture. The **right two-thirds must stay
> visually quiet** — deep shadow, silhouettes, fog, night sky, distant shapes.
> No important detail right of centre; a menu is drawn over it.
>
> **No text, letters, kanji, signatures or watermarks anywhere in the image.**
>
> Japanese setting, night. Export as **PNG** — never JPEG, never inside a PDF.

---

## The scene

*The fiction, if you want it in one line: the moon over the rice paddies has
gone the colour of old bone, the flock has turned, and one retainer is still
standing at the gate.*

> A lone duck samurai stands in the left third of the frame, seen from the side
> in three-quarter view, naginata planted in the mud, straw cape and lacquered
> armour, back to the viewer's left and facing right into the dark. Moonlight
> rims his silhouette in cold white. Around his feet, flooded rice paddies
> reflect a bone-coloured moon in still black water; broken shrine posts and
> reeds break the surface. To the right the ground falls away into fog and
> deep indigo shadow, and in that shadow the shapes of the rotting flock are
> only barely suggested — a dozen hunched silhouettes, pale eye-glints, no
> detail. A vermilion torii gate stands half-drowned at the far left edge.
> Palette: bone white, cold moon blue, deep indigo, rot green, one vermilion
> accent. Ominous, still, and quiet on the right.

---

## Variants worth trying

Same SPEC, different mood — generate a few and pick.

**1. 暁 — Dawn Watch.** Same figure, but the sky behind is the first grey of
dawn rather than night. He has survived one. Cold gold on the horizon at the
far left, the flock receding into mist on the right.

**2. 崩 — The Breach.** Mid-fight. The retainer is lower in frame, braced,
naginata swung; two or three rotting ducks are close enough to read in the left
third while the rest stay as shadow. More vermilion, more motion, same quiet
right side.

**3. 社 — The Shrine Steps.** The retainer seen small, from behind, at the foot
of a long flight of moss-covered stone steps rising left-to-right into fog. The
flock as silhouettes on the steps above him. Emptier, lonelier, very quiet.

**4. 面 — The Mask.** Extreme close crop: just the duck's head and shoulders in
the left third, kabuto and menpō, one eye catching the moon. Everything else is
fog and dark. Strongest for a small screen.

---

## When it comes back

Send the **PNG** and I'll wire it in. It becomes the menu backdrop in place of
the live board, so it does not need to match the battlefield's geometry — no
lanes, no grid, no reserved bank. The only hard requirements are the dimensions,
the quiet right side, and no lettering.

If you like one enough to want the hero animated over it — head bobbing to the
soundtrack like the units do — say so and send it **in two layers**, the scene
without the duck and the duck alone on transparency, exactly as we did for the
battlefield props. That worked, and flattened art cannot be separated afterwards.
