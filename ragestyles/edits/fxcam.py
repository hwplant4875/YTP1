"""Per-frame camera + hit effects for one shot (OpenCV), streamed ffmpeg -> python -> ffmpeg.

Camera: subject-centred crop (cx, cy as fractions of the source), base zoom, a slow push-in over the
whole shot ("kb"), and punch-in hits that ramp in 0.18 s (smoothstep) and then hold.
Hit flash: pixel*(1+k) + 18k, k = amount * curve, curve rises 0.06 s and falls to 0 at 0.5 s (smoothstep).
Strong hits add a red luminance wash (0.5 -> 0 over 0.45 s) and a 14 px R/B chromatic split (-> 0 over 0.35 s).
"""
import subprocess, numpy as np, cv2


def ease(u):
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3 - 2 * u)


def flash_curve(dt, rise=0.06, total=0.5):
    if dt < 0 or dt > total:
        return 0.0
    if dt < rise:
        return float(ease(dt / rise))
    return float(1 - ease((dt - rise) / (total - rise)))


def grade(f, g):
    """'4K edit' look (CapCut/TikTok style), all on float BGR 0-255:
    clarity = local contrast on luminance (large-radius unsharp), contrast = S-curve around mid grey,
    saturation boost, then two-radius sharpen (fine detail + structure)."""
    if not g:
        return f
    exp, lift = g.get('exposure', 0), g.get('brightness', 0)
    if exp or lift:
        # exposure gain (stops) with a soft highlight shoulder, then a gamma lift of the mids
        x = np.clip(f / 255.0, 0, 1) * 2 ** exp
        knee = 0.85
        over = np.maximum(x - knee, 0)
        x = np.where(x > knee, knee + (1 - knee) * (1 - np.exp(-over / (1 - knee))), x)
        x = x ** (1 / (1 + lift))
        f = 255 * x
    clar = g.get('clarity', 0.35)
    if clar:
        lum = f.mean(axis=2)
        f = f + clar * (lum - cv2.GaussianBlur(lum, (0, 0), 18))[..., None]
    c = g.get('contrast', 0.12)
    if c:
        x = np.clip(f / 255.0, 0, 1)
        s_curve = x * x * (3 - 2 * x)
        f = 255 * (x + c * (s_curve - x) * 2)
    sat = g.get('saturation', 0.08)
    if sat:
        lum = f.mean(axis=2, keepdims=True)
        f = lum + (f - lum) * (1 + sat)
    for sigma, amt in ((0.8, g.get('sharpen', 0.7)), (2.2, g.get('structure', 0.35))):
        if amt:
            f = f + amt * (f - cv2.GaussianBlur(f, (0, 0), sigma))
    return f


def lerp2(v, u):
    if isinstance(v, (list, tuple)):
        return v[0] + (v[1] - v[0]) * float(ease(u))
    return v


def render_shot(src, t_in, dur, pre_filter, shot, out_w, out_h, out_path, bg=(0, 0, 0), fps=30, crf=14, preset='medium', grade_cfg=None):
    vf = (pre_filter + ',' if pre_filter else '') + f'fps={fps}'
    # frame size after the pre-filter
    sz = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t_in:.3f}', '-i', src, '-frames:v', '1', '-vf', vf,
                         '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    first = cv2.imdecode(np.frombuffer(sz, np.uint8), cv2.IMREAD_COLOR)
    sh, sw = first.shape[:2]
    n = int(round(dur * fps))
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t_in:.3f}', '-t', f'{dur + 0.2:.3f}', '-i', src, '-vf', vf,
                            '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{out_w}x{out_h}', '-r', str(fps),
                            '-i', '-', '-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-pix_fmt', 'yuv420p', out_path],
                           stdin=subprocess.PIPE)
    if grade_cfg:
        # brighten dark footage only: full lift below ~0.22 mean luma, none above ~0.42 (bright shots glare otherwise);
        # washed-out footage (mean above ~0.62) is pulled down a little instead
        m = first.mean() / 255.0
        k = float(np.clip((0.42 - m) / 0.2, 0, 1))
        tame = -0.25 * float(np.clip((m - 0.62) / 0.15, 0, 1))
        grade_cfg = dict(grade_cfg, exposure=grade_cfg.get('exposure', 0.2) * k + tame,
                         brightness=grade_cfg.get('brightness', 0.12) * k)
    wide = shot.get('fit') == 'wide'
    out_aspect = out_w / out_h
    hits = shot.get('hits', [])
    kb = shot.get('kb', 0.06)
    last = None
    for i in range(n):
        buf = dec.stdout.read(sw * sh * 3)
        if len(buf) == sw * sh * 3:
            last = np.frombuffer(buf, np.uint8).reshape(sh, sw, 3)
        img = last
        t = i / fps
        u = t / dur
        # zoom: base * slow push * held punches
        z = shot.get('zoom', 1.0) * (1 + kb * float(ease(u)))
        for h in hits:
            z *= 1 + (h.get('zoom', 1.08) - 1) * float(ease((t - h['t']) / 0.18))
        # zoom-through transition: the outgoing shot rushes in over its last `zt` s,
        # the incoming shot starts at the same over-zoom and settles back to its framing
        zt = shot.get('zt', 0.16)
        if shot.get('zout'):
            z *= 1 + (shot['zout'] - 1) * float(ease((t - (dur - zt)) / zt))
        if shot.get('zin'):
            z *= 1 + (shot['zin'] - 1) * (1 - float(ease(t / (zt * 1.4))))
        cx = lerp2(shot.get('cx', 0.5), u) * sw
        cy = lerp2(shot.get('cy', 0.5), u) * sh
        if wide:
            # whole source width fills the window width at z=1; letterbox top/bottom
            cw = sw / z
            s = out_w / cw
            ch = out_h / s
        else:
            # fill: largest window-aspect crop that fits the source, divided by z
            if sw / sh > out_aspect:
                ch0, cw0 = sh, sh * out_aspect
            else:
                cw0, ch0 = sw, sw / out_aspect
            cw, ch = cw0 / z, ch0 / z
            s = out_w / cw
        cx = min(max(cx, cw / 2), sw - cw / 2) if cw <= sw else sw / 2
        cy = min(max(cy, ch / 2), sh - ch / 2) if ch <= sh else sh / 2
        M = np.float32([[s, 0, out_w / 2 - s * cx], [0, s, out_h / 2 - s * cy]])
        frame = cv2.warpAffine(img, M, (out_w, out_h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT, borderValue=bg)
        f = frame.astype(np.float32)
        blur = cv2.GaussianBlur(f, (0, 0), 1.3)
        if grade_cfg is None:
            f = f + shot.get('sharpen', 0.55) * (f - blur)
        else:
            f = grade(f, grade_cfg)
        for h in hits:
            dt = t - h['t']
            k = h.get('amount', 0.5) * flash_curve(dt)
            if k > 0:
                f = f * (1 + k) + 18 * k
            if h.get('strong') and 0 <= dt <= 0.45:
                w = 0.5 * (1 - float(ease(dt / 0.45)))
                lum = cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
                red = np.dstack([lum * 0.18, lum * 0.22, np.minimum(lum * 1.25 + 20, 255)])
                f = f * (1 - w) + red * w
            if h.get('strong') and 0 <= dt <= 0.35:
                sh_px = 14 * (1 - float(ease(dt / 0.35)))
                if sh_px > 0.3:
                    b, g, r = cv2.split(f)
                    r = cv2.warpAffine(r, np.float32([[1, 0, sh_px], [0, 1, 0]]), (out_w, out_h), borderMode=cv2.BORDER_REPLICATE)
                    b = cv2.warpAffine(b, np.float32([[1, 0, -sh_px], [0, 1, 0]]), (out_w, out_h), borderMode=cv2.BORDER_REPLICATE)
                    f = cv2.merge([b, g, r])
        enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.kill()
