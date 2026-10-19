import { chromium } from 'playwright';
import { FONTS } from './eng.mjs';
// usage: node still.mjs module fn t '{"opts":1}' out.png
const [mod, fn, t, opts, out] = process.argv.slice(2);
const m = await import('./' + mod);
const svg = m[fn](Number(t), JSON.parse(opts || '{}')) + '</svg>';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${FONTS}body{margin:0;background:#000}</style>${svg}`); await p.waitForTimeout(150);
await p.screenshot({ path: out }); await b.close();
