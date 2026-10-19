import { chromium } from 'playwright'; import { FONTS, K } from '/tmp/claude-0/sp2/eng2.mjs'; import { bgAir } from '/tmp/claude-0/hb/bird.mjs';
import * as A from './ha.mjs';
const s = bgAir(0) + A.fly(400, 300, 0.5, 0.03) + A.branch(700, 1100, 390) + A.perched(900, 280, 0.45, {}) + A.perched(1300, 280, 0.45, { puff: 1, closed: 1 })
 + A.flowerT(1700, 250, 1, {glowUV:0}) + A.flowerT(1500, 450, 0.8, {glowUV:1}) + A.bee(300, 700, 1, 0.1) + A.coin(600, 750, 90) + A.scale(1000, 750, '3 G') + A.gauge(1500, 750, 150, 0.9, { lab: 'POWER', lo: 'E', hi: 'F' })
 + A.ecg(100, 900, 1000, 0.3, 1.5, {amp:90}) + A.timer(1800, 950, 60, 0.65) + A.blossom(1200, 980, 50) + A.birdHeart(1750, 600, 2) + A.heartIcon(1350, 980, 0.6);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<style>${FONTS}body{margin:0}</style><svg width="1920" height="1080">${s}</svg>`); await p.waitForTimeout(100); await p.screenshot({ path: 'chk/props.png' }); await b.close();
