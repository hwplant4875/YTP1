"""Adapters for the episode's 2D graphics when reused in shorts (loaded by assemble.py via the visual's "module")."""
import graphics2d as g


def c19_short(args, d, timing, base, out):
    """c19 'stations' map for a line that only says 'sixteen stations'. g_c19 lights each closed station when the
    narration names it; here none is named, so hand it a placeholder beat (starting after the clip, never shown) that
    "names" all sixteen at the moment 'sixteen' is said: they all light together with their ripple."""
    t16 = g.word_time(timing, "sixteen")
    names = " ".join(n[:-2] if n.endswith((" U", " S")) else n for n in g.GHOSTS)
    far = {"start": 1e9, "end": 1e9, "say_at": t16 - 0.12, "say_d": 0.0, "say": "S-Bahn: Nordbahnhof " + names}
    # the "16 GHOST STATIONS" counter sits in the top-right corner, under the Shorts top bar: move it down
    dy = args.get("counter_dy", 0)
    panel, text = g.panel, g.text
    def panel2(img, box, *a, **k):
        if dy and box[1] == 30:
            box = (box[0], box[1] + dy, box[2], box[3] + dy)
            return panel(img, box, alpha=235)   # nearly opaque: the moved counter sits over map lettering
        return panel(img, box, *a, **k)
    def text2(dr, xy, s, *a, **k):
        if dy and xy[0] == g.W - 70 and xy[1] in (100, 180):
            xy = (xy[0], xy[1] + dy)
        return text(dr, xy, s, *a, **k)
    g.panel, g.text = panel2, text2
    try:
        g.g_c19({k: v for k, v in args.items() if k != "counter_dy"}, d, list(timing) + [far], base, out)
    finally:
        g.panel, g.text = panel, text


GRAPHICS = {"c19_short": c19_short}
