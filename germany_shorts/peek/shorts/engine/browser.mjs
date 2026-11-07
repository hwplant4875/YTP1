import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import { serve } from './serve.mjs';
// Open a page (path relative to repo root) at WxH, wait for window.READY.
export async function openPage(rel, W = 1080, H = 1920, query = '') {
  const { srv, port } = await serve();
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(`http://127.0.0.1:${port}/${rel}?w=${W}&h=${H}${query ? '&' + query : ''}`);
  await page.waitForFunction(() => window.READY === true || window.ERROR, null, { timeout: 120000 });
  const err = await page.evaluate(() => window.ERROR || null);
  if (err || errs.length) { console.error('PAGE ERROR', err, errs.join('\n')); }
  return { browser, page, srv, errs, async close() { await browser.close(); srv.close(); } };
}
