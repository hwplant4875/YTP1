// Big YouTube-style captions: YouTube Sans Black, white (or one highlight colour) with a thick black stroke.
export class TextLayer {
  constructor(root, W, H) { this.root = root; this.W = W; this.H = H; this.items = new Map(); this.used = new Set(); }
  begin() { this.used.clear(); }
  set(name, o) {
    let it = this.items.get(name);
    if (!it) {
      const el = document.createElement('div'); el.className = 'tx';
      const s = document.createElement('div'); s.className = 's';
      const f = document.createElement('div'); f.className = 'f';
      el.append(s, f); this.root.append(el);
      it = { el, s, f, key: '' }; this.items.set(name, it);
    }
    this.used.add(name);
    const size = o.size || 120;
    const key = [o.text, size, o.y, o.color, o.x || 0].join('|');
    if (key !== it.key) {
      it.key = key;
      it.s.textContent = o.text; it.f.textContent = o.text;
      it.el.style.fontSize = size + 'px';
      it.el.style.top = o.y + 'px';
      it.el.style.height = (size * 1.2 * (String(o.text).split('\n').length)) + 'px';
      it.el.style.left = (o.x || 0) + 'px';
      it.el.style.setProperty('--c', o.color || '#fff');
      it.el.style.setProperty('--sw', Math.round(size * (o.stroke || 0.13)) + 'px');
    }
    const sc = o.scale ?? 1, op = o.opacity ?? 1, dy = o.dy || 0;
    it.el.style.transform = `translateY(${dy}px) scale(${sc})`;
    it.el.style.transformOrigin = `50% ${size * 0.5}px`;
    it.el.style.opacity = op;
    it.el.style.display = op > 0.001 ? 'block' : 'none';
  }
  end() { for (const [n, it] of this.items) if (!this.used.has(n)) it.el.style.display = 'none'; }
}
