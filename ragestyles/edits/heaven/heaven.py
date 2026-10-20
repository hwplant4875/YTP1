"""'Gone to heaven' meme: a cut-out object rises up the stairs of the heaven image into the light, with a glow,
a golden halo, twinkles and a caption.   python3 heaven.py cutout.png heaven.png out.mp4 [dur] [caption]
An out.png writes one still instead: the object already up in the light, halo on, no twinkles."""
import os, subprocess, sys
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from rewind import W, H, FPS, caption_rgba, ease, over  # noqa: E402

FONT = '/home/user/rs_work/fonts/YOUTUBESANSBLACK.OTF'


def cover(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return np.asarray(im.convert('RGB').crop((x, y, x + W, y + H))).astype(np.float32)


def paste(dst, rgba, cx, cy, a=1.0):
    h, w = rgba.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    src = rgba[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    k = src[..., 3:4] / 255 * a
    dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - k) + src[..., :3] * k


def main(cut, bgp, out, dur=2.8, cap='RIP iPhone 😭'):
    obj = np.asarray(Image.open(cut).convert('RGBA'))
    ys, xs = np.nonzero(obj[..., 3] > 20)
    obj = obj[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s0 = 760 / obj.shape[0]
    obj = cv2.resize(obj, None, fx=s0, fy=s0, interpolation=cv2.INTER_AREA)
    pad = 120
    obj = np.pad(obj, ((pad, pad), (pad, pad), (0, 0)))
    al = obj[..., 3].astype(np.float32)
    glow = cv2.GaussianBlur(cv2.dilate(al, np.ones((25, 25))), (0, 0), 30)
    glow = np.dstack([np.full_like(al, 255)] * 3 + [np.clip(glow * 1.6, 0, 255)]).astype(np.uint8)
    halo = np.zeros((140, 420, 4), np.uint8)
    cv2.ellipse(halo, (210, 70), (150, 34), 0, 0, 360, (255, 214, 90, 255), 16, cv2.LINE_AA)
    hg = cv2.GaussianBlur(halo, (0, 0), 9)
    halo = np.maximum(halo, (hg * np.array([1, 1, 1, 1.4])).clip(0, 255).astype(np.uint8))
    bg0 = cover(Image.open(bgp))
    capr = caption_rgba(FONT, cap, 1470, 96)
    rng = np.random.default_rng(3)
    stars = [(rng.uniform(-330, 330), rng.uniform(-380, 380), rng.uniform(0, 2.4), rng.uniform(8, 18)) for _ in range(14)]
    still = out.lower().endswith('.png')
    n = 1 if still else int(dur * FPS)
    p = None if still else subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for j in range(n):
        t = 2.0 if still else j / FPS
        z = 1 + 0.06 * t / dur
        bg = cv2.resize(bg0, None, fx=z, fy=z)
        oy, ox = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
        fr = bg[oy:oy + H, ox:ox + W].copy()
        e = ease(min(t / 2.0, 1))
        cy = 1560 - 700 * e + (0 if still else 14 * np.sin(t * 3.2))
        sc = 1.0 - 0.18 * e
        ang = 0 if still else 5 * np.sin(t * 2.1)
        M = cv2.getRotationMatrix2D((obj.shape[1] / 2, obj.shape[0] / 2), ang, sc)
        o = cv2.warpAffine(obj, M, (obj.shape[1], obj.shape[0]), flags=cv2.INTER_LINEAR)
        g = cv2.warpAffine(glow, M, (obj.shape[1], obj.shape[0]), flags=cv2.INTER_LINEAR)
        paste(fr, g, W / 2, cy, 0.85 if still else 0.75 + 0.2 * np.sin(t * 5))
        paste(fr, o, W / 2, cy)
        ha = min(max((t - 0.5) / 0.4, 0), 1)
        paste(fr, halo, W / 2, cy - (obj.shape[0] / 2 - pad) * sc - 40, ha)
        for sx, sy, t0, r in ([] if still else stars):
            k = np.sin(np.pi * ((t - t0) % 1.2) / 1.2) if t > t0 else 0
            if k > 0.05:
                c = (int(W / 2 + sx), int(cy + sy))
                for d in ((r * k, 0), (0, r * k * 1.6)):
                    cv2.line(fr, (int(c[0] - d[0]), int(c[1] - d[1])), (int(c[0] + d[0]), int(c[1] + d[1])),
                             (255, 255, 240), 3, cv2.LINE_AA)
        fr = np.clip(fr, 0, 255).astype(np.uint8)
        if t > 0.35:
            fr = over(fr, capr)
        if still:
            Image.fromarray(fr).save(out)
            return
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], *(float(sys.argv[4]),) if len(sys.argv) > 4 else (), *sys.argv[5:6])
