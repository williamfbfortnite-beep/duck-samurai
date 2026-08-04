/* Cut assets/ui/*.png out of the generated UI sheet.
 *
 *   node tools/uikit.mjs [path/to/sheet.png]     (defaults to assets/ui/_sheet.png)
 *
 * The sheet is kept in the repo alongside the pieces on purpose: this ran twice
 * out of a scratch directory that was reset under it, and without the source
 * the cut is not reproducible — you cannot re-slice, re-quantise, or pull a
 * piece nobody wanted the first time.
 *
 * Three things about the sheet drive everything below, all of them properties
 * of what the generator returned rather than choices:
 *
 *   1. Its transparency is painted on. The file is 100% opaque; that
 *      checkerboard is drawn into the image and has to be keyed out.
 *   2. It is not limited-palette art. A 200x60 button carries ~1,700 distinct
 *      colours, so it is quantised — which is what makes it read as pixel art,
 *      not just what makes it small.
 *   3. It is dithered, so nine-slice bands cannot be found by looking for rows
 *      that repeat. Nothing repeats byte for byte.
 */
import fs from 'fs';
import zlib from 'zlib';
import path from 'path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.join(ROOT, 'assets', 'ui');
const SRC = process.argv[2] || path.join(OUT, '_sheet.png');

/* Which piece of the sheet becomes which file, by index into the piece list the
   keying pass finds, plus the nine-slice inset to use. Insets come from the
   measurement below; they are rounded to one number per piece where the art is
   symmetric, because a nine-slice that differs top from bottom by 2px just
   looks like a mistake. The two `.big` frames share 24 so that a button does
   not resize when it lights up. */
const USE = [
  [1,  'btn',        13],  // dark plum, thin gold frame   — button at rest
  [0,  'btn-big',    24],  // wide dark, corner brackets    — menu button
  [5,  'btn-big-on', 24],  // wide parchment                — menu button engaged
  [10, 'panel',      27],  // ornate double frame           — crates, tracks, sound box
  [24, 'slim',       12],  // rounded thin frame            — pills, cards, tooltips, rows
  [13, 'slot',       21],  // ribbed dark, gold brackets    — crate-reveal cards
  [9,  'rule',        0],  // divider with a diamond boss   — under section titles
  [21, 'tick',        0],  // check badge                   — picked
  [22, 'lock',        0],  // padlock                       — locked / sealed
  /* The four ornaments sit as a 2x2 block on the sheet — left column top and
     bottom, right column top and bottom — so the bottom pair reads the same
     way round as the top pair. Taking them in the wrong order put a
     bottom-right ornament in the bottom-left slot and vice versa. */
  [17, 'corner-tl',   0], [18, 'corner-tr', 0],
  [25, 'corner-bl',   0], [26, 'corner-br', 0]
];

// ── read ────────────────────────────────────────────────────────────────────
function readPNG(file) {
  const b = fs.readFileSync(file);
  const W = b.readUInt32BE(16), H = b.readUInt32BE(20), ct = b[25];
  if (ct !== 6 && ct !== 2) throw new Error(`${file}: colour type ${ct} not supported (want RGB or RGBA)`);
  const idat = [];
  for (let p = 8; p < b.length; ) {
    const l = b.readUInt32BE(p), t = b.toString('ascii', p + 4, p + 8);
    if (t === 'IDAT') idat.push(b.subarray(p + 8, p + 8 + l));
    p += 12 + l; if (t === 'IEND') break;
  }
  const ch = ct === 6 ? 4 : 3, raw = zlib.inflateSync(Buffer.concat(idat));
  const st = W * ch, px = Buffer.alloc(st * H);
  let o = 0;
  for (let y = 0; y < H; y++) {
    const f = raw[o++], c = raw.subarray(o, o + st); o += st;
    for (let i = 0; i < st; i++) {
      const a = i >= ch ? px[y*st + i - ch] : 0, u = y ? px[(y-1)*st + i] : 0,
            ul = (i >= ch && y) ? px[(y-1)*st + i - ch] : 0;
      let v = c[i];
      if (f === 1) v += a; else if (f === 2) v += u; else if (f === 3) v += (a + u) >> 1;
      else if (f === 4) { const q = a + u - ul, pa = Math.abs(q-a), pb = Math.abs(q-u), pc = Math.abs(q-ul);
        v += (pa <= pb && pa <= pc) ? a : (pb <= pc ? u : ul); }
      px[y*st + i] = v & 255;
    }
  }
  return { W, H, ch, px };
}

// ── key out the painted checkerboard ────────────────────────────────────────
/* Two flat neutral greys against art that is either coloured or much darker.
   Flood every large blob of it, wherever it sits: seeding only from the border
   cannot reach the checkerboard enclosed by the panel frames, and leaves their
   interiors painted grey. */
function key({ W, H, ch, px }) {
  const isChecker = (r, g, b) =>
    Math.abs(r-g) <= 8 && Math.abs(g-b) <= 8 && Math.abs(r-b) <= 8 && r >= 108 && r <= 215;
  const bg = new Uint8Array(W * H), seen = new Uint8Array(W * H), st = [];
  let cut = 0, blobs = 0;
  for (let p0 = 0; p0 < W * H; p0++) {
    if (seen[p0]) continue;
    const i0 = p0 * ch;
    if (!isChecker(px[i0], px[i0+1], px[i0+2])) { seen[p0] = 1; continue; }
    st.push(p0); seen[p0] = 1;
    const run = [];
    while (st.length) {
      const p = st.pop(); run.push(p);
      const y = (p / W) | 0, x = p % W;
      for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1]]) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
        const q = ny * W + nx; if (seen[q]) continue;
        const i = q * ch; if (!isChecker(px[i], px[i+1], px[i+2])) continue;
        seen[q] = 1; st.push(q);
      }
    }
    if (run.length >= 400) { blobs++; for (const p of run) { bg[p] = 1; cut++; } }
  }
  const out = Buffer.alloc(W * H * 4);
  for (let i = 0; i < W * H; i++) {
    out[i*4] = px[i*ch]; out[i*4+1] = px[i*ch+1]; out[i*4+2] = px[i*ch+2];
    out[i*4+3] = bg[i] ? 0 : 255;
  }
  console.log(`keyed ${blobs} checkerboard regions — ${(cut / (W*H) * 100).toFixed(1)}% of the sheet`);
  return out;
}

// ── separate the pieces ─────────────────────────────────────────────────────
function pieces(W, H, rgba) {
  const A = i => rgba[i*4 + 3];
  const lab = new Int32Array(W * H).fill(-1), boxes = [], st = [];
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const p = y*W + x; if (!A(p) || lab[p] >= 0) continue;
    const id = boxes.length; let n = 0, x0 = x, x1 = x, y0 = y, y1 = y;
    st.push(p); lab[p] = id;
    while (st.length) {
      const c = st.pop(), cy = (c / W) | 0, cx = c % W; n++;
      if (cx < x0) x0 = cx; if (cx > x1) x1 = cx; if (cy < y0) y0 = cy; if (cy > y1) y1 = cy;
      // a 3px reach bridges the gaps a dithered outline leaves inside one piece
      for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
        const nx = cx + dx, ny = cy + dy;
        if (nx < 0 || nx >= W || ny < 0 || ny >= H) continue;
        const r = ny*W + nx; if (A(r) && lab[r] < 0) { lab[r] = id; st.push(r); }
      }
    }
    if (n > 600) boxes.push({ x: x0, y: y0, w: x1-x0+1, h: y1-y0+1 });
  }
  boxes.sort((a, b) => (a.y >> 5) - (b.y >> 5) || a.x - b.x);   // reading order, row-banded
  return boxes;
}

/* Nine-slice insets. The usual trick — find the run of identical rows that make
   up the repeating edge — finds nothing, because the art is dithered and no two
   adjacent lines match. Comparing each line to the middle of the piece by mean
   distance fails too: a corner ornament is a large difference confined to the
   ends of a 290px row, and averaging buries it. Count the *fraction* of pixels
   that genuinely disagree instead; that does not care how wide the row is. */
function measure(W, rgba, b) {
  const at = (x, y) => { const i = (y*W + x) * 4; return [rgba[i], rgba[i+1], rgba[i+2], rgba[i+3]]; };
  const diff = (get, n) => (p, q) => {
    let bad = 0;
    for (let i = 0; i < n; i++) {
      const u = get(p, i), v = get(q, i);
      if (u[3] !== v[3] || Math.abs(u[0]-v[0]) > 40 || Math.abs(u[1]-v[1]) > 40 || Math.abs(u[2]-v[2]) > 40) bad++;
    }
    return bad / n;
  };
  const TOL = 0.02;
  const rd = diff((y, i) => at(b.x + i, b.y + y), b.w);
  const cd = diff((x, i) => at(b.x + x, b.y + i), b.h);
  const my = b.h >> 1, mx = b.w >> 1;
  let t = 0; while (t < my && rd(t, my) > TOL) t++;
  let bo = 0; while (bo < my && rd(b.h - 1 - bo, my) > TOL) bo++;
  let l = 0; while (l < mx && cd(l, mx) > TOL) l++;
  let r = 0; while (r < mx && cd(b.w - 1 - r, mx) > TOL) r++;
  return { t, r, b: bo, l };
}

// ── quantise ────────────────────────────────────────────────────────────────
/* Median cut. The sheet is painterly with per-pixel noise, not the flat palette
   it looks like from a distance, so collapsing it onto ~48 colours is what
   makes it read as pixel art — the size win is a side effect. */
function quantise(counts, n) {
  let boxes = [[...counts.keys()].map(k => k.split(',').map(Number))];
  const range = box => {
    const lo = [255,255,255], hi = [0,0,0];
    for (const c of box) for (let i = 0; i < 3; i++) { if (c[i] < lo[i]) lo[i] = c[i]; if (c[i] > hi[i]) hi[i] = c[i]; }
    return [0,1,2].map(i => hi[i] - lo[i]);
  };
  while (boxes.length < n) {
    let pick = -1, axis = 0, best = 0;
    boxes.forEach((box, i) => {
      if (box.length < 2) return;
      const rg = range(box), ax = rg.indexOf(Math.max(...rg));
      // weight by population, so a big flat area earns entries a stray speck can't
      const pop = box.reduce((s, c) => s + counts.get(c.join(',')), 0);
      const score = rg[ax] * Math.cbrt(pop);
      if (score > best) { best = score; pick = i; axis = ax; }
    });
    if (pick < 0) break;
    const box = boxes[pick].slice().sort((a, b) => a[axis] - b[axis]);
    boxes.splice(pick, 1, box.slice(0, box.length >> 1), box.slice(box.length >> 1));
  }
  return boxes.filter(b => b.length).map(box => {
    let n = 0, s = [0, 0, 0];
    for (const c of box) { const w = counts.get(c.join(',')); n += w;
      for (let i = 0; i < 3; i++) s[i] += c[i] * w; }
    return s.map(v => Math.round(v / n));
  });
}

// ── write ───────────────────────────────────────────────────────────────────
const CRC = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
const crc = b => { let c = 0xffffffff; for (const v of b) c = CRC[(c ^ v) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (ty, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length);
  const td = Buffer.concat([Buffer.from(ty, 'ascii'), d]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td));
  return Buffer.concat([l, td, c]); };

/* Per-row filter chosen by the standard minimum-sum-of-absolute-differences
   heuristic — on dithered art it beats filter 0 by about a third. */
function filterRows(rows, w) {
  const out = Buffer.alloc((w + 1) * rows.length);
  let prev = Buffer.alloc(w);
  rows.forEach((row, y) => {
    let best = null, bestScore = Infinity;
    for (let f = 0; f < 5; f++) {
      const line = Buffer.alloc(w); let score = 0;
      for (let i = 0; i < w; i++) {
        const a = i >= 1 ? row[i-1] : 0, b = prev[i], c = i >= 1 ? prev[i-1] : 0;
        let v;
        if (f === 0) v = row[i]; else if (f === 1) v = row[i] - a;
        else if (f === 2) v = row[i] - b; else if (f === 3) v = row[i] - ((a + b) >> 1);
        else { const p = a + b - c, pa = Math.abs(p-a), pb = Math.abs(p-b), pc = Math.abs(p-c);
               v = row[i] - (pa <= pb && pa <= pc ? a : pb <= pc ? b : c); }
        line[i] = v & 0xff; score += Math.min(line[i], 256 - line[i]);
      }
      if (score < bestScore) { bestScore = score; best = [f, line]; }
    }
    out[y * (w + 1)] = best[0];
    best[1].copy(out, y * (w + 1) + 1);
    prev = row;
  });
  return out;
}

function encode(w, h, get, maxColours = 48) {
  const counts = new Map();                       // keying leaves alpha binary
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const [r, g, b, a] = get(x, y); if (!a) continue;
    const k = `${r},${g},${b}`; counts.set(k, (counts.get(k) || 0) + 1);
  }
  const table = quantise(counts, maxColours);
  const nearest = new Map(); let errSum = 0, errMax = 0, errN = 0;
  const lookup = (r, g, b) => {
    const k = `${r},${g},${b}`; let i = nearest.get(k);
    if (i === undefined) {
      let bd = Infinity;
      table.forEach((c, j) => { const d = (c[0]-r)**2 + (c[1]-g)**2 + (c[2]-b)**2; if (d < bd) { bd = d; i = j; } });
      nearest.set(k, i);
      const n = counts.get(k); errSum += Math.sqrt(bd) * n; errN += n;
      if (Math.sqrt(bd) > errMax) errMax = Math.sqrt(bd);
    }
    return i;
  };
  const pal = new Map(), idx = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const [r, g, b, a] = get(x, y);
    const k = a === 0 ? 'x' : String(lookup(r, g, b));      // every clear pixel is one entry
    let i = pal.get(k); if (i === undefined) { i = pal.size; pal.set(k, i); }
    idx[y*w + x] = i;
  }
  if (pal.size > 256) throw new Error(`quantiser produced ${pal.size} entries — cannot index`);

  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 3;
  const plte = Buffer.alloc(pal.size * 3), trns = Buffer.alloc(pal.size, 255);
  for (const [k, i] of pal) {
    if (k === 'x') { trns[i] = 0; continue; }
    const [r, g, b] = table[+k]; plte[i*3] = r; plte[i*3+1] = g; plte[i*3+2] = b;
  }
  let last = trns.length; while (last > 0 && trns[last-1] === 255) last--;   // tRNS may be truncated
  const rows = []; for (let y = 0; y < h; y++) rows.push(Buffer.from(idx.subarray(y*w, y*w + w)));
  return {
    png: Buffer.concat([Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]),
      chunk('IHDR', ihdr), chunk('PLTE', plte), ...(last ? [chunk('tRNS', trns.subarray(0, last))] : []),
      chunk('IDAT', zlib.deflateSync(filterRows(rows, w), { level: 9 })), chunk('IEND', Buffer.alloc(0))]),
    colours: pal.size, err: { mean: errN ? errSum / errN : 0, max: errMax }
  };
}

// ── run ─────────────────────────────────────────────────────────────────────
const sheet = readPNG(SRC);
console.log(`${path.relative(ROOT, SRC)} — ${sheet.W}x${sheet.H}`);
const rgba = key(sheet);
const boxes = pieces(sheet.W, sheet.H, rgba);
console.log(`${boxes.length} separable pieces\n`);

fs.mkdirSync(OUT, { recursive: true });
let total = 0;
console.log('  file          size      measured t/r/b/l   used  colours    KB   shift');
for (const [i, name, slice] of USE) {
  const b = boxes[i];
  if (!b) throw new Error(`piece ${i} (${name}) not found — the sheet or the keying has changed`);
  const m = measure(sheet.W, rgba, b);
  const get = (x, y) => { const s = ((b.y + y) * sheet.W + b.x + x) * 4;
    return [rgba[s], rgba[s+1], rgba[s+2], rgba[s+3]]; };
  const { png, colours, err } = encode(b.w, b.h, get);
  if (slice && Math.max(m.t, m.r, m.b, m.l) > b.h / 2)
    throw new Error(`${name}: measured inset exceeds half its height — wrong piece?`);
  fs.writeFileSync(path.join(OUT, name + '.png'), png);
  total += png.length;
  console.log(`  ${name.padEnd(12)} ${String(b.w).padStart(3)}x${String(b.h).padEnd(3)}   ` +
    `${String(m.t).padStart(3)} ${String(m.r).padStart(3)} ${String(m.b).padStart(3)} ${String(m.l).padStart(3)}` +
    `      ${String(slice).padStart(3)}  ${String(colours).padStart(4)}   ${(png.length/1024).toFixed(1).padStart(5)}` +
    `   ${err.mean.toFixed(1)}/${err.max.toFixed(0)}`);
}
console.log(`\n${USE.length} files, ${(total/1024).toFixed(0)} KB ` +
  `(${(total*4/3/1024).toFixed(0)} KB once base64'd into the artifact)`);
console.log('the "used" column is what game.html passes to border-image-slice');
