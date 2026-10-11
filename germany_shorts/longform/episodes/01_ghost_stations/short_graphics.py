"""Adapters for the episode's 2D graphics when reused in shorts (loaded by assemble.py via the visual's "module")."""
import graphics2d as g


def c19_short(args, d, timing, base, out):
    """c19 'stations' map for a line that only says 'sixteen stations'. g_c19 lights each closed station when the
    narration names it; here none is named, so hand it a placeholder beat (starting after the clip, never shown) that
    "names" all sixteen at the moment 'sixteen' is said: they all light together with their ripple."""
    t16 = g.word_time(timing, "sixteen")
    names = " ".join(n[:-2] if n.endswith((" U", " S")) else n for n in g.GHOSTS)
    far = {"start": 1e9, "end": 1e9, "say_at": t16 - 0.12, "say_d": 0.0, "say": "S-Bahn: Nordbahnhof " + names}
    g.g_c19(args, d, list(timing) + [far], base, out)


GRAPHICS = {"c19_short": c19_short}
