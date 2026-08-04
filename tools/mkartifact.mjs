/* Build the artifact-shaped page from game.html.
 *
 * This lives in the repo on purpose. It used to sit in a scratch directory,
 * which was reset twice in one session — and each time it came back missing
 * inlining steps, built without complaint, and produced a page silently
 * missing the prop layer and half the audio.
 *
 * It used to inline from a hand-kept table of asset paths, which caught that
 * class of bug but only for the paths someone remembered to list — and it only
 * ever looked at the body, so the UI kit's `url('assets/ui/…')` references in
 * the stylesheet would have sailed straight through it. It now finds every
 * quoted assets/ path in the whole document instead. Nothing has to be
 * registered, and the guard at the bottom fails the build rather than shipping
 * a page with a dead asset path in it.
 *
 * Artifacts are wrapped in <!doctype html><head></head><body> at publish time,
 * so this emits body-level content only: <title>, <style>, markup, <script>.
 */
import fs from 'fs';
import path from 'path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = process.argv[2];
if (!OUT) { console.error('usage: node tools/mkartifact.mjs <output.html>'); process.exit(1); }

const src = fs.readFileSync(path.join(ROOT, 'game.html'), 'utf8');
const title = src.match(/<title>([\s\S]*?)<\/title>/)[1];
const style = src.match(/<style>([\s\S]*?)<\/style>/)[1];
const body = src.match(/<body>([\s\S]*?)<\/body>/)[1];
for (const [name, v] of [['title', title], ['style', style], ['body', body]])
  if (!v || !v.trim()) throw new Error('empty ' + name);
if (!body.includes('<script>') || !body.includes('id="cv"')) throw new Error('body missing script or canvas');

let out = `<title>${title}</title>

<style>
/* The artifact wrapper owns the root elements; the game commits to one dark
   visual world, so pin the ground in both themes rather than inheriting. */
:root, :root[data-theme="light"], :root[data-theme="dark"] { color-scheme: dark; }
html, body { background: #070410 !important; }
${style}</style>
${body}`;

/* A relative path cannot survive publication — the artifact CSP blocks every
   external host — so every one of these has to become a data URI. */
const MIME = { png: 'image/png', mp3: 'audio/mpeg' };
const found = new Map();
out = out.replace(/(['"])(assets\/[A-Za-z0-9_/-]+\.(png|mp3))\1/g, (_, q, rel, ext) => {
  let uri = found.get(rel);
  if (!uri) {
    const abs = path.join(ROOT, rel);
    if (!fs.existsSync(abs)) throw new Error(`game.html references ${rel}, which does not exist`);
    const b64 = fs.readFileSync(abs).toString('base64');
    uri = `data:${MIME[ext]};base64,${b64}`;
    found.set(rel, uri);
    console.log(`  inlined ${rel.padEnd(24)} ${(b64.length / 1024).toFixed(0).padStart(6)} KB of base64`);
  }
  return q + uri + q;
});
if (!found.size) throw new Error('no assets inlined at all — the reference pattern has stopped matching');

fs.writeFileSync(OUT, out);

for (const bad of ['<!DOCTYPE', '<html', '<head>', '<body>', '</body>', '</html>'])
  if (out.includes(bad)) throw new Error('leaked wrapper tag: ' + bad);
const leak = out.match(/assets\/[A-Za-z0-9_/-]+\.(?:png|mp3)/);
if (leak) throw new Error(`asset not inlined: ${leak[0]} still referenced`);

console.log(`  no wrapper tags leaked, ${found.size} assets inlined, none left by path`);
console.log(`  wrote ${OUT} (${(out.length / 1024 / 1024).toFixed(1)} MB)`);
