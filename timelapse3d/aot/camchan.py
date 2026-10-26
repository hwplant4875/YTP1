"""Camera channels for the one-take EP1 camera (SCENE_BIBLE_v2 A3).  Pure Python + numpy, NO bpy: runs in and out of Blender.

    Channel(T, pts, v_in=None, v_out=None)   render_fast._Channel (chord-scaled Hermite + PCHIP arc-length re-timing) with
                                             optional velocity vectors (m/s) at the first / last key (moving seams)
    CamPath(keys, v_in, v_out, look_v_in, look_v_out)   keys = [(t, cam_xyz, look_xyz, lens_mm), ...]
        .eval(t) -> (loc, look, lens)   .vel(t) -> m/s (finite difference)
    check(path, t0, t1, ground, dt, limits)   peak speed / yaw rate / pitch / height / lens + FLAGS (prints, returns dict)

    python aot/camchan.py --check g8          one camkeys segment (or: all, or a run: A1 A2 B)
    python aot/camchan.py --check all --report design_specs/camcheck_report.md

Without v_in / v_out a Channel equals render_fast._Channel (first tangent from rest, last = last secant).  With v_in the
curve leaves the first key along v_in at |v_in| m/s; with v_out it arrives along v_out at |v_out| m/s (a zero vector = at rest).
"""
import math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

def _len(a): return float(np.sqrt(np.dot(a, a)))

def _herm(p0, p1, p2, p3, u, m1=None, m2=None):
    """Hermite segment p1->p2 with Catmull-Rom tangents scaled by the chord lengths (m1 / m2 override the tangents)."""
    d01, d12, d23 = _len(p1 - p0), _len(p2 - p1), _len(p3 - p2)
    if m1 is None:
        m1 = (p2 - p0) * (d12 / (d01 + d12)) if d01 + d12 > 1e-9 else p2 - p1
    if m2 is None:
        m2 = (p3 - p1) * (d12 / (d12 + d23)) if d12 + d23 > 1e-9 else p2 - p1
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return p1 * h00 + m1 * h10 + p2 * h01 + m2 * h11

def pchip_m(T, S, m0=None, m1=None):
    """Fritsch-Carlson tangents: monotone cubic through (T_i, S_i); first tangent 0 (rest) / last = last secant unless given."""
    D = [(S[i + 1] - S[i]) / (T[i + 1] - T[i]) for i in range(len(T) - 1)]
    m = [0.0] + [0.0 if D[i - 1] * D[i] <= 0 else 2 * D[i - 1] * D[i] / (D[i - 1] + D[i]) for i in range(1, len(D))] + [D[-1]]
    if m0 is not None: m[0] = m0
    if m1 is not None: m[-1] = m1
    return m

def pchip(T, S, m, t):
    t = min(max(t, T[0]), T[-1])
    i = int(min(len(T) - 2, max(0, np.searchsorted(T, t, side="right") - 1)))
    h = T[i + 1] - T[i]; s = (t - T[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    return h00 * S[i] + h10 * h * m[i] + h01 * S[i + 1] + h11 * h * m[i + 1]

class Channel:
    """One camera channel (location or look-at point): chord-scaled Hermite path through the keys, re-timed by a monotone
    time -> arc-length curve so its speed is C1-smooth in time.  v_in / v_out: optional end velocities (m/s)."""
    def __init__(self, T, pts, v_in=None, v_out=None):
        self.T = np.asarray(T, float); self.P = [np.asarray(p, float) for p in pts]
        n = len(pts); self.segs = []; S = [0.0]; self.notes = []
        vi = None if v_in is None else np.asarray(v_in, float)
        vo = None if v_out is None else np.asarray(v_out, float)
        for i in range(n - 1):
            q = [self.P[max(0, min(n - 1, j))] for j in (i - 1, i, i + 1, i + 2)]
            d12 = _len(q[2] - q[1]); m1 = m2 = None
            if i == 0 and vi is not None and _len(vi) > 1e-9: m1 = vi / _len(vi) * d12
            if i == n - 2 and vo is not None and _len(vo) > 1e-9: m2 = vo / _len(vo) * d12
            N = 96 if m1 is None and m2 is None else 1536      # finer arc table where a seam velocity must match to <1 %
            acc = [0.0]; prev = q[1]
            for k in range(1, N + 1):
                p = _herm(*q, k / N, m1, m2)
                acc.append(acc[-1] + _len(p - prev) + 1e-7); prev = p
            self.segs.append((q, np.asarray(acc), m1, m2, N)); S.append(S[-1] + acc[-1])
        self.S = S; self.total = S[-1]
        m0 = None if vi is None else _len(vi)
        mn = None if vo is None else _len(vo)
        self.m = pchip_m(self.T, S, m0, mn)
        D = [(S[i + 1] - S[i]) / (self.T[i + 1] - self.T[i]) for i in range(n - 1)]
        if m0 and m0 > 3 * D[0]: self.notes.append("v_in %.1f m/s > 3x first mean speed %.1f: arc length may overshoot" % (m0, D[0]))
        if mn and mn > 3 * D[-1]: self.notes.append("v_out %.1f m/s > 3x last mean speed %.1f: arc length may overshoot" % (mn, D[-1]))
    def s_at(self, t):
        return pchip(self.T, self.S, self.m, t)
    def at_s(self, s):
        nseg = len(self.segs)
        i = int(min(nseg - 1, max(0, np.searchsorted(self.S[:nseg], s + 1e-9, side="right") - 1)))
        q, acc, m1, m2, N = self.segs[i]; r = s - self.S[i]
        k = int(min(len(acc) - 2, max(0, np.searchsorted(acc, r, side="left") - 1)))
        f = min(1.0, max(0.0, (r - acc[k]) / (acc[k + 1] - acc[k])))
        return _herm(*q, (k + f) / N, m1, m2)
    def at(self, t):
        return self.at_s(self.s_at(t))

def speed_profile(v0, v1, t_ramp, t_cruise_end, t_end):
    """Progress fraction f(t) in [0,1] for a drive: ramp v0 -> v1 over t_ramp, cruise to t_cruise_end, one constant
    deceleration to rest at t_end (bible g3 flight).  Use as CamPath(profile=...)."""
    a1 = (v1 - v0) / t_ramp; d1 = (v0 + v1) / 2 * t_ramp; d2 = v1 * (t_cruise_end - t_ramp)
    td = t_end - t_cruise_end; D = d1 + d2 + v1 * td / 2
    def f(t):
        t = min(max(t, 0.0), t_end)
        if t <= t_ramp: d = v0 * t + a1 * t * t / 2
        elif t <= t_cruise_end: d = d1 + v1 * (t - t_ramp)
        else:
            u = t - t_cruise_end; d = d1 + d2 + v1 * u - v1 * u * u / (2 * td)
        return d / D
    return f

class CamPath:
    """keys = [(t, cam_xyz, look_xyz, lens_mm), ...].  Separate position / look-at arc-length channels, lens in log space
    (first and last lens rate 0).  v_in / v_out: camera velocity at the first / last key; look_v_in / look_v_out: the look-at
    point's.  profile: optional f(t) -> progress fraction (0..1) of the position path that re-times the whole camera
    (e.g. speed_profile for the g3 flight); t outside the key range is clamped."""
    def __init__(self, keys, v_in=None, v_out=None, look_v_in=None, look_v_out=None, profile=None):
        self.keys = list(keys)
        self.T = np.array([k[0] for k in self.keys], float)
        self.loc = Channel(self.T, [k[1] for k in self.keys], v_in, v_out)
        self.tgt = Channel(self.T, [k[2] for k in self.keys], look_v_in, look_v_out)
        self.lnl = [math.log(k[3]) for k in self.keys]
        self.ml = pchip_m(self.T, self.lnl, None, 0.0)
        self.profile = profile
        self.t0, self.t1 = float(self.T[0]), float(self.T[-1])
        self.notes = self.loc.notes + self.tgt.notes
    def _tau(self, t):
        t = min(max(t, self.t0), self.t1)
        if not self.profile: return t
        goal = self.profile(t - self.t0) * self.loc.total; lo, hi = self.t0, self.t1
        for _ in range(48):
            mid = (lo + hi) / 2
            if self.loc.s_at(mid) < goal: lo = mid
            else: hi = mid
        return (lo + hi) / 2
    def eval(self, t):
        tau = self._tau(t)
        return self.loc.at(tau), self.tgt.at(tau), math.exp(pchip(self.T, self.lnl, self.ml, tau))
    def vel(self, t, h=1 / 120):
        a, b = max(self.t0, t - h), min(self.t1, t + h)
        return (self.eval(b)[0] - self.eval(a)[0]) / (b - a)

# ------------------------------------------------------------------------------------------------ checker
LIMITS = dict(speed=150.0, yaw=30.0, pitch=(17.0, 45.0), hmin=90.0, hmax=650.0, hmin_from=None, lens=(27.0, 50.0),
              under=15.0, flip=90.0, name="")

def check(path, t0=None, t1=None, ground=lambda x, y: 0.0, dt=1 / 60, limits=None, quiet=False):
    """Sample path at 1/dt, print + return peak speed (m/s, time), peak yaw rate (deg/s, time), pitch range, min height above
    ground, lens range and FLAGS: look-at passing under the camera (horizontal distance cam->look < limits['under'] m or a yaw
    rate > limits['flip']), speed / yaw over the limits, height outside hmin..hmax (only from t >= hmin_from), pitch / lens
    outside their ranges.  Override any limit per call (limits=dict(...)); None disables one."""
    L = dict(LIMITS); L.update(limits or {})
    t0 = path.t0 if t0 is None else t0; t1 = path.t1 if t1 is None else t1
    n = int(round((t1 - t0) / dt)); ts = t0 + np.arange(n + 1) * dt
    E = [path.eval(t) for t in ts]
    C = np.array([e[0] for e in E]); T = np.array([e[1] for e in E]); LN = np.array([e[2] for e in E])
    sp = np.linalg.norm(np.diff(C, axis=0), axis=1) / dt
    d = T - C; hor = np.hypot(d[:, 0], d[:, 1])
    yaw = np.degrees(np.arctan2(d[:, 1], d[:, 0])); dy = np.diff(yaw); dy = (dy + 180) % 360 - 180; yr = np.abs(dy) / dt
    pitch = np.degrees(np.arctan2(-d[:, 2], np.maximum(hor, 1e-9)))
    h = np.array([c[2] - ground(c[0], c[1]) for c in C])
    hf = L["hmin_from"]; hm = (ts >= (hf if hf is not None else -1e9))
    r = dict(name=L["name"], t0=t0, t1=t1, peak_speed=float(sp.max()), t_peak_speed=float(ts[sp.argmax()]),
             peak_yaw=float(yr.max()), t_peak_yaw=float(ts[yr.argmax()]), pitch_min=float(pitch.min()), pitch_max=float(pitch.max()),
             hmin=float(h[hm].min()), t_hmin=float(ts[hm][h[hm].argmin()]), hmax=float(h.max()),
             lens_min=float(LN.min()), lens_max=float(LN.max()), min_hor=float(hor.min()), t_min_hor=float(ts[hor.argmin()]),
             flags=[], notes=list(path.notes))
    F = r["flags"]
    def span(mask):
        idx = np.where(mask)[0]
        return "%.2f-%.2f s" % (ts[idx[0]], ts[idx[-1]]) if len(idx) else ""
    if L["under"] and r["min_hor"] < L["under"]:
        F.append("LOOK-UNDER: horizontal cam->look %.1f m < %g at t=%.2f (%s)" % (r["min_hor"], L["under"], r["t_min_hor"], span(hor < L["under"])))
    if L["flip"] and r["peak_yaw"] > L["flip"]:
        F.append("YAW-FLIP: %.0f deg/s at t=%.2f" % (r["peak_yaw"], r["t_peak_yaw"]))
    if L["speed"] and r["peak_speed"] > L["speed"] * 1.005:
        F.append("SPEED: %.1f m/s > %g at t=%.2f" % (r["peak_speed"], L["speed"], r["t_peak_speed"]))
    if L["yaw"] and r["peak_yaw"] > L["yaw"] * 1.005 and not (L["flip"] and r["peak_yaw"] > L["flip"]):
        F.append("YAW: %.1f deg/s > %g at t=%.2f" % (r["peak_yaw"], L["yaw"], r["t_peak_yaw"]))
    if L["hmin"] is not None and r["hmin"] < L["hmin"] - 0.5:
        F.append("HEIGHT-LOW: %.0f m < %g at t=%.2f (%s)" % (r["hmin"], L["hmin"], r["t_hmin"], span(hm & (h < L["hmin"] - 0.5))))
    if L["hmax"] is not None and r["hmax"] > L["hmax"]:
        F.append("HEIGHT-HIGH: %.0f m > %g (%s)" % (r["hmax"], L["hmax"], span(h > L["hmax"])))
    if L["pitch"] and (r["pitch_min"] < L["pitch"][0] - 0.5 or r["pitch_max"] > L["pitch"][1] + 0.5):
        F.append("PITCH: %.0f..%.0f deg outside %g..%g (%s)" % (r["pitch_min"], r["pitch_max"], L["pitch"][0], L["pitch"][1],
                 span((pitch < L["pitch"][0] - 0.5) | (pitch > L["pitch"][1] + 0.5))))
    if L["lens"] and (r["lens_min"] < L["lens"][0] - 0.1 or r["lens_max"] > L["lens"][1] + 0.1):
        F.append("LENS: %.1f..%.1f mm outside %g..%g" % (r["lens_min"], r["lens_max"], L["lens"][0], L["lens"][1]))
    if not quiet:
        print("%s  t %.2f..%.2f s" % (L["name"] or "camera", t0, t1))
        print("  peak speed %.1f m/s @ %.2f s | peak yaw %.1f deg/s @ %.2f s | pitch %.0f..%.0f deg | height %.0f m (min @ %.2f s) .. %.0f m | lens %.1f..%.1f mm"
              % (r["peak_speed"], r["t_peak_speed"], r["peak_yaw"], r["t_peak_yaw"], r["pitch_min"], r["pitch_max"], r["hmin"], r["t_hmin"],
                 r["hmax"], r["lens_min"], r["lens_max"]))
        for x in r["notes"]: print("  NOTE", x)
        print("  FLAGS: " + ("none" if not F else ""))
        for f in F: print("   -", f)
    return r

# ------------------------------------------------------------------------------------------------ CLI
def _report(rows, out):
    f = lambda x: "-" if x is None else x
    md = ["# Camera check report (aot/camchan.py)", "",
          "Generated by `python aot/camchan.py --check all --report design_specs/camcheck_report.md` from `aot/camkeys.py` (bible keys transcribed as written, tight times).",
          "Sampled at 60 Hz. Limits (bible A3): yaw <= 30 deg/s, speed <= 150 m/s (g3 flight: its explicit profile), height 90-650 m (per-segment exceptions listed), pitch 17-45 deg (51 cutaway), lens 27-50 mm.", "",
          "| run / segment | t (s) | peak m/s (@t) | bible m/s | peak deg/s (@t) | bible deg/s | pitch | height min..max (m) | lens | flags |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for name, r, q in rows:
        md.append("| %s | %.1f-%.1f | %.0f (%.1f) | %s | %.1f (%.1f) | %s | %.0f..%.0f | %.0f (%.1f)..%.0f | %.1f-%.1f | %s |" % (
            name, r["t0"], r["t1"], r["peak_speed"], r["t_peak_speed"], f(q.get("bible_speed")), r["peak_yaw"], r["t_peak_yaw"],
            f(q.get("bible_yaw")), r["pitch_min"], r["pitch_max"], r["hmin"], r["t_hmin"], r["hmax"], r["lens_min"], r["lens_max"],
            "; ".join(x.split(":")[0] for x in r["flags"]) or "none"))
    md += ["", "## Flag details", ""]
    for name, r, q in rows:
        if r["flags"] or r["notes"] or q.get("comment"):
            md.append("### " + name)
            for x in r["flags"]: md.append("- FLAG " + x)
            for x in r["notes"]: md.append("- NOTE " + x)
            if q.get("comment"): md.append("- " + q["comment"])
            md.append("")
    import camkeys as CK
    md += ["## Comparison with the bible and notes", ""] + ["- " + x for x in CK.NOTES]
    open(out, "w", encoding="utf8").write("\n".join(md) + "\n")
    print("wrote", out)

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--check" not in a:
        print(__doc__); sys.exit(0)
    sys.path.insert(0, HERE)
    import camkeys as CK
    what = a[a.index("--check") + 1]
    names = CK.ALL_CHECKS if what == "all" else [what]
    rows = []
    for nm in names:
        p, kw, q = CK.path(nm)
        r = check(p, limits=dict(name=nm, **kw.get("limits", {})), t0=kw.get("t0"), t1=kw.get("t1")); rows.append((nm, r, q)); print()
    if "--report" in a:
        _report(rows, os.path.abspath(a[a.index("--report") + 1]))
