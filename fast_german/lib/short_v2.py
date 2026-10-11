"""Fast German short, v2 look (user feedback 2026-10-11 on 02):
- no captions; the centre graphics carry the lesson (big, clean, nothing tiny)
- every element fits inside the frame with margins (no cut-off letters)
- real photos mixed in with graphics
- German is spoken with German pronunciation (C.tts(lang="de")), English by the same voice; speed 1.0

Spec: {"id", "music"?, "scenes": [{"lines": [[seg, ...], ...], "els": [el, ...]}]}
  seg = {"de": "Tor."} | {"en": "for gate."}, optional "show": [el ids] revealed when the segment starts
  el  = {"id", "type": photo|word|row|grid|logo, ...}; els without "show" appear at scene start
"""
import json, math, os, re, subprocess, sys, tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import common as C

W, H, FPS = 1080, 1920, 30
MX = 80                      # side margin: nothing may come closer to the frame edge
LINE_GAP, SEG_GAP, SCENE_GAP = 0.32, 0.10, 0.45
NAVY_T, NAVY_B = (22, 27, 58), (10, 12, 28)
WHITE, GREY = (250, 250, 247), (178, 184, 204)
PHOTOS = "/mnt/project-files/fast_german/cache/photos/"
FD = "/mnt/project-files/fonts/de/"
UI = "/mnt/project-files/fonts/YouTubeSans-Black.otf"
MUSIC = [os.path.join(C.CACHE, "music", n + ".mp3") for n in ("kpop_beat_a", "kpop_beat_c", "rave_c")]
MUSIC_VOL, POP_VOL = 0.17, 0.16   # SFX far under the voice (user rule 2026-10-11)


def de_font(size):
    return ImageFont.truetype(FD + "BarlowCondensed-ExtraBold.ttf", size)


def ui_font(size):
    return ImageFont.truetype(UI, size)


def fit(text, fnt, max_w, start, lo=40):
    s = start
    while s > lo and fnt(s).getlength(text) > max_w:
        s -= 4
    return fnt(s)


def text_im(text, f, fill, stroke=0, sfill=(0, 0, 0)):
    l, t, r, b = f.getbbox(text, stroke_width=stroke)
    im = Image.new("RGBA", (r - l + 8, b - t + 8))
    ImageDraw.Draw(im).text((4 - l, 4 - t), text, font=f, fill=fill + (255,), stroke_width=stroke,
                            stroke_fill=sfill + (255,))
    return im


def shadow(im, r=22, a=120, dy=12):
    pad = r * 2
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    m = Image.new("L", out.size, 0)
    m.paste(im.split()[3].point(lambda v: v * a // 255), (pad, pad + dy))
    sh.putalpha(m.filter(ImageFilter.GaussianBlur(r)))
    out.alpha_composite(sh)
    out.alpha_composite(im, (pad, pad))
    return out


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def cover(src, w, h, focus=(0.5, 0.5)):
    im = Image.open(src).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    x = int((im.width - w) * focus[0])
    y = int((im.height - h) * focus[1])
    return im.crop((x, y, x + w, y + h))


def photo_card(src, w, h, focus=(0.5, 0.5), border=10):
    """Photo in a white-edged rounded card. Rendered 8% larger so the slow push-in never shows edges."""
    big = cover(PHOTOS + src, int(w * 1.08), int(h * 1.08), focus)
    return big, (w, h, border)


def word_block(de, article=None, en=None, max_w=W - 2 * MX, size=200, colour=None, show_article=True):
    """German word (article in its gender colour) with the English meaning under it, fitted to max_w."""
    col = colour or WHITE
    acol = C.GENDER.get(article, WHITE) if article else None
    full = (article + " " + de) if (article and show_article) else de
    f = fit(full, de_font, max_w, size)
    lead = (article + " ") if (article and show_article) else ""
    l, t, r, b = f.getbbox(full)
    word_im = Image.new("RGBA", (r - l + 8, b - t + 8))
    d = ImageDraw.Draw(word_im)
    if lead:
        d.text((4 - l, 4 - t), lead, font=f, fill=lighten(acol) + (255,))
    d.text((4 - l + f.getlength(lead), 4 - t), de, font=f, fill=(col if not article or colour else WHITE) + (255,))
    parts, wsum, hmax = [word_im], word_im.width, word_im.height
    en_im = None
    if en:
        fe = fit(en, ui_font, max_w, int(f.size * 0.36), 30)
        en_im = text_im(en, fe, GREY)
    out_h = hmax + (en_im.height + 18 if en_im else 0)
    out_w = max(wsum, en_im.width if en_im else 0)
    out = Image.new("RGBA", (out_w, out_h))
    x = (out_w - wsum) // 2
    for p in parts:
        out.alpha_composite(p, (x, hmax - p.height))
        x += p.width
    if en_im:
        out.alpha_composite(en_im, ((out_w - en_im.width) // 2, hmax + 18))
    return out


def lighten(c, k=0.18):
    return tuple(int(v + (255 - v) * k) for v in c)


def thumb(el, s):
    if el.get("photo"):
        return rounded(cover(PHOTOS + el["photo"], s, s, tuple(el.get("focus", (0.5, 0.5)))), 34)
    tile = Image.new("RGBA", (s, s))
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, s - 1, s - 1), 34, fill=(255, 255, 255, 30))
    ic = C.icon(el["icon"], int(s * 0.74))
    tile.alpha_composite(ic, ((s - ic.width) // 2, (s - ic.height) // 2))
    return tile


def row_im(el, w=W - 2 * MX, s=250):
    """One line of a stacked breakdown: picture | German word (gender colour) = English."""
    im = Image.new("RGBA", (w, s))
    im.alpha_composite(thumb(el, s), (0, 0))
    art = el.get("article") if el.get("show_article") else None
    col = C.GENDER.get(el.get("article")) if el.get("article") else WHITE
    tx = s + 44
    f = fit((art + " " if art else "") + el["de"], de_font, w - tx, 150)
    lead = (art + " ") if art else ""
    l, t, r, b = f.getbbox(lead + el["de"])
    d = ImageDraw.Draw(im)
    wc = (lighten(col) if el.get("article") else WHITE) + (255,)
    if lead:
        d.text((tx - l, 18 - t), lead, font=f, fill=wc)
    d.text((tx - l + f.getlength(lead), 18 - t), el["de"], font=f, fill=wc)
    if el.get("en"):
        fe = fit(el["en"], ui_font, w - tx, 78, 30)
        e = text_im(el["en"], fe, (255, 214, 120))
        im.alpha_composite(e, (tx, s - e.height - 22))
    if el.get("hl"):
        hl = Image.new("RGBA", (w + 40, s + 40))
        ImageDraw.Draw(hl).rounded_rectangle((0, 0, w + 39, s + 39), 44, outline=lighten(col) + (255,), width=8)
        hl.alpha_composite(im, (20, 20))
        return hl
    return im


def logo_im():
    p = Image.open("/mnt/project-files/fast_german/branding/final/profile_night_pretzel_filled.png").convert("RGB")
    p = p.resize((420, 420), Image.LANCZOS)
    m = Image.new("L", p.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, 419, 419), fill=255)
    out = p.convert("RGBA")
    out.putalpha(m)
    return out


def background():
    y = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array(NAVY_T, np.float32), np.array(NAVY_B, np.float32)
    g = top * (1 - y) + bot * y
    xx = np.linspace(-1, 1, W)[None, :, None]
    yy = np.linspace(-1, 1, H)[:, None, None]
    g = g * (1 - 0.25 * np.clip(xx ** 2 + (yy * 0.6) ** 2, 0, 1))
    rng = np.random.default_rng(3)
    g = g + rng.normal(0, 2.2, (H, W, 1))
    bg = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(bg)
    for _ in range(90):  # faint stars, same night sky as the profile picture
        x, yv = rng.integers(0, W), rng.integers(0, H)
        r = rng.choice([1, 1, 2])
        d.ellipse((x - r, yv - r, x + r, yv + r), fill=(255, 255, 255, int(rng.integers(40, 110))))
    tag = text_im("FAST GERMAN", de_font(46), (255, 214, 120))
    bg.alpha_composite(tag, ((W - tag.width) // 2, 150))
    return bg


def build_el(el):
    t = el["type"]
    if t == "photo":
        return ("photo",) + photo_card(el["src"], el["w"], el["h"], tuple(el.get("focus", (0.5, 0.5))))
    if t == "word":
        return ("img", shadow(word_block(el["de"], el.get("article"), el.get("en"), el.get("max_w", W - 2 * MX),
                                          el.get("size", 200), tuple(el["colour"]) if el.get("colour") else None),
                              24, 150, 8))
    if t == "row":
        return ("img", row_im(el))
    if t == "tile":
        s = el["s"]
        return ("img", shadow(thumb(el, s) if el.get("photo") or el.get("icon") else label_tile(el, s), 20, 140, 10))
    if t == "logo":
        return ("img", shadow(logo_im(), 30, 160, 10))
    if t == "text":
        f = fit(el["text"], ui_font, W - 2 * MX, el.get("size", 84))
        return ("img", text_im(el["text"], f, tuple(el.get("colour", WHITE))))
    raise ValueError(t)


def label_tile(el, s):
    tile = Image.new("RGBA", (s, s))
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, s - 1, s - 1), 34, fill=(255, 214, 120, 255))
    f = fit(el["label"], de_font, s - 50, 120)
    t = text_im(el["label"], f, (20, 22, 40))
    tile.alpha_composite(t, ((s - t.width) // 2, (s - t.height) // 2))
    return tile


def ease(t):
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return 1 - (1 - t) ** 3


def draw_el(frame, built, el, local, appear, scene_len):
    p = ease((local - appear) / 0.32)
    if p <= 0:
        return
    cx, cy = el["x"], el["y"]
    if built[0] == "photo":
        big, (w, h, border) = built[1], built[2]
        z = 1.0 + 0.06 * min(1, max(0, local) / max(1.0, scene_len))     # slow push-in, kept inside the card
        crop_w, crop_h = big.width / z, big.height / z
        x0, y0 = (big.width - crop_w) / 2, (big.height - crop_h) / 2
        img = big.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + crop_w, y0 + crop_h))
        card = Image.new("RGBA", (w + 2 * border, h + 2 * border))
        ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 40, fill=(255, 255, 255, 255))
        card.alpha_composite(rounded(img, 32), (border, border))
        im = shadow(card, 26, 150, 14)
    else:
        im = built[1]
    sc = 0.9 + 0.1 * p
    if sc < 0.999:
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if p < 1:
        a = im.split()[3].point(lambda v: int(v * p))
        im = im.copy()
        im.putalpha(a)
    dy = int((1 - p) * 40)
    frame.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 + dy)))


def german_take(text):
    """German clip with a falling ending: try a few stabilities, keep the first whose ending falls.
    Pitch is only measured, never edited (user rule 2026-10-10)."""
    import parselmouth
    best = None
    for st in (0.45, 0.55, 0.65, 0.35):
        mp3, _ = C.tts(text, stability=st, lang="de")
        wav = mp3[:-4] + ".wav"
        if not os.path.exists(wav):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, wav], check=True)
        f = parselmouth.Sound(wav).to_pitch().selected_array["frequency"]
        f = f[f > 0]
        if len(f) < 10:
            return mp3
        rise = 12 * np.log2(np.median(f[-8:]) / np.median(f[: len(f) // 2]))
        if best is None or rise < best[1]:
            best = (mp3, rise)
        if rise < -1.5 or not text.rstrip().endswith("."):
            return mp3
    return best[0]


def render(spec_path, out_path):
    spec = json.load(open(spec_path))
    t = 0.4
    clips, timeline, pops = [], [], []
    for sc in spec["scenes"]:
        start = t
        shows = {}
        for line in sc["lines"]:
            for seg in line:
                if "pause" in seg:
                    t += seg["pause"]
                    continue
                for e in seg.get("show", []):
                    shows[e] = t - start
                    pops.append(t)
                mp3 = german_take(seg["de"]) if "de" in seg else C.tts(seg["en"])[0]
                clips.append((mp3, t))
                t += C.duration(mp3) + SEG_GAP
            t += LINE_GAP - SEG_GAP
        t += sc.get("hold", 0)
        timeline.append({"scene": sc, "start": start, "end": t, "shows": shows})
        t += SCENE_GAP
    total = t + 0.4
    # audio
    tmp = tempfile.mkdtemp()
    inputs, fl = [], []
    for i, (mp3, st) in enumerate(clips):
        inputs += ["-i", mp3]
        fl.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={int(st * 1000)}:all=1[c{i}]")
    n = len(clips)
    fl.append("".join(f"[c{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total},"
              f"atrim=0:{total},loudnorm=I=-15:TP=-2:LRA=11,asplit=2[voice][key]")
    k, mix = n, []
    pop = C.get_sfx("pop")
    for at in pops:
        inputs += ["-i", pop]
        fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={POP_VOL},"
                  f"adelay={int(max(0, at - 0.03) * 1000)}:all=1[f{k}]")
        mix.append(f"[f{k}]")
        k += 1
    num = int(re.match(r"\d*", os.path.basename(spec_path)).group() or 0)
    music = spec.get("music") or MUSIC[num % len(MUSIC)]
    inputs += ["-stream_loop", "-1", "-i", music]
    fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{total},afade=t=in:d=0.5,"
              f"afade=t=out:st={total - 1.2}:d=1.2,volume={MUSIC_VOL}[m0]")
    fl.append("[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[music]")
    mix.append("[music]")
    fl.append("[voice]" + "".join(mix) + f"amix=inputs={1 + len(mix)}:normalize=0,alimiter=limit=0.89[a]")
    wav = os.path.join(tmp, "a.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fl), "-map", "[a]",
                    "-t", f"{total:.3f}", wav], check=True)
    # frames
    bg = background()
    built = [{e["id"]: build_el(e) for e in tl["scene"]["els"]} for tl in timeline]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "warning", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset",
                           "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    for fi in range(int(total * FPS)):
        now = fi / FPS
        si = max([i for i, tl in enumerate(timeline) if tl["start"] - 0.15 <= now] or [0])
        tl = timeline[si]
        first = min([tl["shows"].get(e["id"], e.get("at", 0.0) - 0.1) for e in tl["scene"]["els"]])
        if si > 0 and now - tl["start"] < first:      # nothing new on screen yet: keep the last scene up
            si -= 1
            tl = timeline[si]
        frame = bg.copy()
        local = now - tl["start"]
        L = tl["end"] - tl["start"] + SCENE_GAP
        for e in tl["scene"]["els"]:
            draw_el(frame, built[si][e["id"]], e, local, tl["shows"].get(e["id"], e.get("at", 0.0) - 0.1), L)
        rgb = frame.convert("RGB")
        if now < 0.5:                                    # fade up from dark
            rgb = Image.blend(Image.new("RGB", (W, H)), rgb, now / 0.5)
        if now > total - 0.6:
            rgb = Image.blend(rgb, Image.new("RGB", (W, H)), min(1, (now - total + 0.6) / 0.6))
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close()
    ff.wait()
    return total


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2]))
