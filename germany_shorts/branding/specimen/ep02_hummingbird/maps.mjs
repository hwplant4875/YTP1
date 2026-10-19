// land outlines from world-atlas topojson, projected into a screen rectangle (Mercator)
import fs from 'fs';
const decode = (topo) => { const { scale: [sx, sy], translate: [tx, ty] } = topo.transform;
  const arcs = topo.arcs.map(a => { let x = 0, y = 0; return a.map(([dx, dy]) => { x += dx; y += dy; return [x * sx + tx, y * sy + ty]; }); });
  const arc = i => i >= 0 ? arcs[i] : arcs[~i].slice().reverse();
  const ring = r => r.flatMap((i, k) => { const a = arc(i); return k ? a.slice(1) : a; });
  const polys = []; const obj = Object.values(topo.objects)[0];
  const geoms = obj.type === 'GeometryCollection' ? obj.geometries : [obj];
  for (const g of geoms) { if (g.type === 'Polygon') polys.push(g.arcs.map(ring)); if (g.type === 'MultiPolygon') for (const p of g.arcs) polys.push(p.map(ring)); }
  return polys; };
const L110 = decode(JSON.parse(fs.readFileSync('/tmp/claude-0/hb2/land.json')));
const L50 = decode(JSON.parse(fs.readFileSync('/tmp/claude-0/hb2/land50.json')));
const merc = lat => Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360));
// view: lon0..lon1, lat0..lat1 mapped into box x,y,w,h (keeps aspect by fitting width)
export const proj = (v) => { const { lon0, lon1, lat0, lat1, x, y, w, h } = v; const m0 = merc(lat0), m1 = merc(lat1);
  return (lon, lat) => [x + (lon - lon0) / (lon1 - lon0) * w, y + (m1 - merc(lat)) / (m1 - m0) * h]; };
export const landPath = (v, hi = false) => { const P = proj(v); let d = '';
  for (const poly of (hi ? L50 : L110)) for (const r of poly) {
    let inb = r.some(([lo, la]) => lo > v.lon0 - 20 && lo < v.lon1 + 20 && la > v.lat0 - 15 && la < v.lat1 + 15); if (!inb) continue;
    if (r.some(([lo]) => lo > 0) && r.some(([lo]) => lo < 0) && r.some(([lo]) => lo > 150)) continue; // skip dateline-crossing rings (Russia)
    let last = null; r.forEach(([lo, la], i) => { const [px, py] = P(lo, Math.max(-80, Math.min(84, la))); if (!i) d += `M${px.toFixed(1)} ${py.toFixed(1)}`; else if (Math.hypot(px - last[0], py - last[1]) > 0.8) d += `L${px.toFixed(1)} ${py.toFixed(1)}`; else return; last = [px, py]; }); d += 'Z'; }
  return d; };
