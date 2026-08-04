/* Build the artifact-shaped page from game.html.
 *
 * This lives in the repo on purpose. It used to sit in a scratch directory,
 * which was reset twice in one session — and each time it came back missing
 * inlining steps, built without complaint, and produced a page silently
 * missing the prop layer and half the audio. The guard at the bottom now fails
 * the build rather than shipping a page with a dead asset path in it.
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

const b64 = f => fs.readFileSync(path.join(ROOT, 'assets', f)).toString('base64');
/* Each asset, and the exact text that references it. A relative path cannot
   survive publication — the artifact CSP blocks every external host — so any
   entry that fails to match is a build failure, not a warning. */
const ASSETS = [
  ['music.mp3',    'src="assets/music.mp3"',            m => `src="data:audio/mpeg;base64,${m}"`],
  ['music2.mp3',   'src="assets/music2.mp3"',           m => `src="data:audio/mpeg;base64,${m}"`],
  ['gameover.mp3', 'src="assets/gameover.mp3"',         m => `src="data:audio/mpeg;base64,${m}"`],
  ['props.png',    "propImg.src = 'assets/props.png';", m => `propImg.src = 'data:image/png;base64,${m}';`],
  ['map.png',      "mapImg.src = 'assets/map.png';",    m => `mapImg.src = 'data:image/png;base64,${m}';`]
];

let inlined = body;
for (const [file, needle, replace] of ASSETS) {
  const before = inlined;
  const data = b64(file);
  inlined = inlined.replace(needle, replace(data));
  if (inlined === before) throw new Error(`could not inline ${file}: "${needle}" not found in game.html`);
  console.log(`  inlined ${file.padEnd(13)} ${(data.length / 1024 / 1024).toFixed(2)} MB of base64`);
}

const out = `<title>${title}</title>

<style>
/* The artifact wrapper owns the root elements; the game commits to one dark
   visual world, so pin the ground in both themes rather than inheriting. */
:root, :root[data-theme="light"], :root[data-theme="dark"] { color-scheme: dark; }
html, body { background: #070410 !important; }
${style}</style>
${inlined}`;

fs.writeFileSync(OUT, out);

for (const bad of ['<!DOCTYPE', '<html', '<head>', '<body>', '</body>', '</html>'])
  if (out.includes(bad)) throw new Error('leaked wrapper tag: ' + bad);
for (const [file] of ASSETS)
  if (out.includes('assets/' + file)) throw new Error(`asset not inlined: assets/${file} still referenced`);

console.log(`  no wrapper tags leaked, every asset inlined`);
console.log(`  wrote ${OUT} (${(out.length / 1024 / 1024).toFixed(1)} MB)`);
