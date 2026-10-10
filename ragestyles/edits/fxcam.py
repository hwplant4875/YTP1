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


def lerp2(v, u):
    if isinstance(v, (list, tuple)):
        return v[0] + (v[1] - v[0]) * float(ease(u))
    return v


def render_shot(src, t_in, dur, pre_filter, shot, out_w, out_h, out_path, bg=(0, 0, 0), fps=30, crf=14, preset='medium'):
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
        f = f + shot.get('sharpen', 0.55) * (f - blur)
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
