import { chromium } from 'playwright';
const [mod, fn, t, opts, out, w, h] = process.argv.slice(2);
const m = await import('./' + mod);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: Number(w || 1080), height: Number(h || 1920) } });
await p.setContent(`<style>${m.FONTS}body{margin:0;background:#000}</style>${m[fn](Number(t), JSON.parse(opts || '{}'))}`); await p.waitForTimeout(200);
await p.screenshot({ path: out }); await b.close();
