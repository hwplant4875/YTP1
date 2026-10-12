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
# Beige theme (user 2026-10-11: night sky dropped, back to the calm beige). WHITE = main text colour.
WHITE, GREY = (28, 28, 30), (110, 104, 98)
ACCENT = (205, 112, 10)
SHADOW_K = 45                       # shadow strength (%), soft on beige
STROKE = 0                          # outline on German words: white, like the first batch
SK = (255, 255, 255, 255)
EN_STROKE = 0                       # dark outline on English lines over the road
WORD_FILL = (28, 28, 30)


def use_road_theme():
    """Dark moving Autobahn background (user 2026-10-11): light text, yellow meanings, stronger shadows."""
    global WHITE, GREY, ACCENT, SHADOW_K, STROKE, EN_STROKE
    WHITE, GREY, ACCENT, SHADOW_K, STROKE, EN_STROKE = (250, 250, 246), (236, 236, 230), (255, 204, 0), 100, 10, 6
PROFILE = "/mnt/project-files/fast_german/branding/final/PROFILE_FINAL_fast_german.png"
PHOTOS = "/mnt/project-files/fast_german/cache/photos/"
FD = "/mnt/project-files/fonts/de/"
UI = "/mnt/project-files/fonts/YouTubeSans-Black.otf"
MUSIC = [os.path.join(C.CACHE, "music", n + ".mp3") for n in ("kpop_beat_a", "kpop_beat_c", "rave_c")]
MUSIC_VOL, POP_VOL = 0.17, 0.16   # SFX far under the voice (user rule 2026-10-11)
ROW_EXTRA = 34  # gap between a row's German word and its yellow meaning (user 2026-10-11)
CLIP_FADE = 0.3  # fade-out on every voice clip (user rule 2026-10-11: no abrupt cut-offs)


def de_font(size, weight="Bold"):
    """Fredoka, the rounded font of the first batch (user 2026-10-11: 01's text style was the good one)."""
    f = ImageFont.truetype(C.FONT, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def en_font(size):
    return de_font(size, "SemiBold")


def ui_font(size):
    return ImageFont.truetype(UI, size)


def fit(text, fnt, max_w, start, lo=40):
    s = start
    while s > lo and fnt(s).getlength(text) > max_w:
        s -= 4
    return fnt(s)


def text_im(text, f, fill, stroke=None, sfill=(20, 20, 24)):
    stroke = EN_STROKE if stroke is None else stroke
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
    m.paste(im.split()[3].point(lambda v: v * a * SHADOW_K // 25500), (pad, pad + dy))  # soft on beige
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
    col = colour or WORD_FILL
    acol = C.GENDER.get(article, WHITE) if article else None
    full = (article + " " + de) if (article and show_article) else de
    f = fit(full, de_font, max_w, size)
    lead = (article + " ") if (article and show_article) else ""
    l, t, r, b = f.getbbox(full)
    p = 4 + STROKE
    word_im = Image.new("RGBA", (r - l + 2 * p, b - t + 2 * p))
    d = ImageDraw.Draw(word_im)
    if lead:
        d.text((p - l, p - t), lead, font=f, fill=lighten(acol) + (255,), stroke_width=STROKE, stroke_fill=SK)
    d.text((p - l + f.getlength(lead), p - t), de, font=f, fill=(col if not article or colour else WORD_FILL) + (255,),
           stroke_width=STROKE, stroke_fill=SK)
    parts, wsum, hmax = [word_im], word_im.width, word_im.height
    en_im = None
    if en:
        fe = fit(en, en_font, max_w, int(f.size * 0.36), 30)
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


def lighten(c, k=0.0):
    return tuple(int(v + (255 - v) * k) for v in c)


def thumb(el, s):
    if el.get("png"):
        tile = Image.new("RGBA", (s, s))
        ic = Image.open(el["png"]).convert("RGBA")
        ic.thumbnail((int(s * 0.92), int(s * 0.92)), Image.LANCZOS)
        tile.alpha_composite(ic, ((s - ic.width) // 2, (s - ic.height) // 2))
        if el.get("cross"):
            x = Image.open(el["cross"]).convert("RGBA")
            x.thumbnail((int(s * 0.62), int(s * 0.62)), Image.LANCZOS)
            tile.alpha_composite(x, (s - x.width, s - x.height))
        return tile
    if el.get("photo"):
        return rounded(cover(PHOTOS + el["photo"], s, s, tuple(el.get("focus", (0.5, 0.5)))), 34)
    tile = Image.new("RGBA", (s, s))                  # bare emoji, no card (user 2026-10-11)
    ic = C.icon(el["icon"], int(s * 0.92))
    tile.alpha_composite(ic, ((s - ic.width) // 2, (s - ic.height) // 2))
    return tile


def row_im(el, w=W - 2 * MX, s=250):
    """One line of a stacked breakdown: picture | German word (gender colour) = English."""
    im = Image.new("RGBA", (w, s + ROW_EXTRA))
    if el.get("photo"):
        im.alpha_composite(thumb(el, s), (0, 0))
    art = el.get("article") if el.get("show_article") else None
    col = C.GENDER.get(el.get("article")) if el.get("article") else WHITE
    tx = s + 44
    f = fit((art + " " if art else "") + el["de"], de_font, w - tx, 150)
    lead = (art + " ") if art else ""
    l, t, r, b = f.getbbox(lead + el["de"])
    d = ImageDraw.Draw(im)
    wc = (tuple(el["colour"]) if el.get("colour") else lighten(col) if el.get("article") else WORD_FILL) + (255,)
    if lead:
        d.text((tx - l, 18 - t), lead, font=f, fill=wc, stroke_width=STROKE, stroke_fill=SK)
    d.text((tx - l + f.getlength(lead), 18 - t), el["de"], font=f, fill=wc, stroke_width=STROKE, stroke_fill=SK)
    if el.get("en"):
        fe = fit(el["en"], en_font, w - tx, 78, 30)
        e = text_im(el["en"], fe, ACCENT)
        ey = min(18 + (b - t) + ROW_EXTRA, im.height - e.height)  # meaning sits a clear gap under the word
        im.alpha_composite(e, (tx, ey))
    if el.get("hl"):
        hl = Image.new("RGBA", (w + 40, im.height + 40))
        ImageDraw.Draw(hl).rounded_rectangle((0, 0, w + 39, im.height + 39), 44, outline=lighten(col) + (255,), width=8)
        hl.alpha_composite(im, (20, 20))
        return hl
    return im


def logo_im():
    p = Image.open(PROFILE).convert("RGB")
    p = p.resize((420, 420), Image.LANCZOS)
    m = Image.new("L", p.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, 419, 419), fill=255)
    out = p.convert("RGBA")
    out.putalpha(m)
    return out


def background():
    """Plain, clean cream page (user 2026-10-11: no pattern, no road) with the bare pretzel badge."""
    bg = Image.new("RGBA", (W, H), tuple(C.CREAM) + (255,))
    bg.alpha_composite(shadow(C.icon("pretzel", 150), 14, 60, 6), ((W - 150) // 2 - 28, 110 - 28))
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
        if el.get("icon"):
            return ("row", row_im(el, el.get("w", W - 2 * MX)), shadow(thumb(el, 250), 16, 110, 10), 20 if el.get("hl") else 0)
        return ("img", row_im(el, el.get("w", W - 2 * MX)))
    if t == "tile":
        s = el["s"]
        if el.get("icon") or el.get("png"):
            return ("float", shadow(thumb(el, s), 20, 120, 12))
        return ("img", shadow(thumb(el, s) if el.get("photo") or el.get("icon") else label_tile(el, s), 20, 140, 10))
    if t == "logo":
        return ("img", shadow(logo_im(), 30, 160, 10))
    if t == "text":
        f = fit(el["text"], en_font, W - 2 * MX, el.get("size", 84))
        return ("img", text_im(el["text"], f, tuple(el.get("colour", WHITE))))
    if t == "timer":
        return ("timer", el.get("s", 150), el.get("dur", 2.0))
    if t == "ring":
        w, h, lw = el["w"], el["h"], el.get("width", 12)
        im = Image.new("RGBA", (w, h))
        ImageDraw.Draw(im).ellipse((lw, lw, w - lw - 1, h - lw - 1), outline=tuple(el.get("colour", (52, 199, 89))) + (255,), width=lw)
        return ("img", shadow(im, 10, 90, 4))
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
    if built[0] == "timer":
        s, dur = built[1], built[2]
        q = min(1.0, max(0.0, (local - appear) / dur))
        im = Image.new("RGBA", (s, s))
        d = ImageDraw.Draw(im)
        d.ellipse((8, 8, s - 9, s - 9), outline=(255, 255, 255, 70), width=14)
        if q > 0:
            d.arc((8, 8, s - 9, s - 9), -90, -90 + 360 * q, fill=ACCENT + (255,), width=14)
        built = ("img", shadow(im, 8, 80, 4))
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
    if built[0] == "float":                           # gentle bob, like the first batch's icons
        cy += 10 * math.sin(local * 2.2 + (hash(el["id"]) % 7))
    if built[0] == "row":                             # the row's emoji floats on its own
        icon = built[2]
        im = im.copy()
        bob = int(8 * math.sin(local * 2.2 + (hash(el["id"]) % 7)))
        canvas = Image.new("RGBA", (im.width + 80, im.height + 80))
        canvas.alpha_composite(im, (40, 40))
        o = 40 + built[3]
        canvas.alpha_composite(icon, (o + 125 - icon.width // 2, o + 125 + ROW_EXTRA // 2 - icon.height // 2 + bob))
        im = canvas
    sc = 0.9 + 0.1 * p
    if sc < 0.999:
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if p < 1:
        a = im.split()[3].point(lambda v: int(v * p))
        im = im.copy()
        im.putalpha(a)
    dy = int((1 - p) * 40)
    frame.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 + dy)))


_HEADERS = {}


def header_im(text):
    """Part title next to the top-left pretzel in long-form ("Part 1 · Saying hello")."""
    if not text:
        return None
    if text not in _HEADERS:
        _HEADERS[text] = text_im(text, en_font(58), WHITE)
    return _HEADERS[text]


def german_take(text, speed=1.0):
    """German clip with a falling ending: try a few stabilities, keep the first whose ending falls.
    Pitch is only measured, never edited (user rule 2026-10-10)."""
    import parselmouth
    best = None
    for st in (0.45, 0.55, 0.65, 0.35):
        mp3, _ = C.tts(text, speed=speed, stability=st, lang="de")
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


_BOUNDS = {}


def voiced(mp3, floor_db=-42):
    """(first, last) second with audible voice in a clip: the TTS file's own lead-in and tail silence."""
    if mp3 not in _BOUNDS:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
        a = np.abs(np.frombuffer(raw, np.int16).astype(np.float32)) / 32768
        n = len(a) // 160
        rms = 20 * np.log10(np.sqrt((a[: n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-9)
        on = np.where(rms > floor_db)[0]
        _BOUNDS[mp3] = (0.0, len(a) / 16000) if not len(on) else (max(0, on[0] - 1) * 0.01, min(n, on[-1] + 3) * 0.01)
    return _BOUNDS[mp3]


def plan(spec):
    """Timeline of a spec: voice clips with start times, scene windows, pop SFX times, total length, subtitle segments.
    spec "tight": seconds of silence between sentences, measured on the voice itself (news shorts, user 2026-10-12:
    never more than ~0.5 s; words inside one line join with only a breath), first graphic pops at 0 s."""
    tight = spec.get("tight")
    t = 0.0 if tight else 0.4
    clips, timeline, pops, subs = [], [], [], []
    for sc in spec["scenes"]:
        start = t
        shows, hides = {}, {}
        for line in sc["lines"]:
            for seg in line:
                for e in seg.get("hide", []):
                    hides[e] = t - start
                for e in seg.get("show", []):
                    shows[e] = t - start
                    if not seg.get("quiet"):
                        pops.append(t)
                if "pause" in seg:
                    t += seg["pause"]
                    continue
                mp3 = german_take(seg["de"], seg.get("speed", 1.0)) if "de" in seg else C.tts(seg["en"])[0]
                if tight:
                    a, b = voiced(mp3)
                    t = max(t, a + 0.02) if not clips else t
                    clips.append((mp3, t - a))
                    subs.append((round(t, 3), round(t + b - a, 3), seg.get("de") or seg["en"], "de" in seg))
                    t += b - a + seg.get("join", 0.07)
                    continue
                clips.append((mp3, t))
                subs.append((round(t, 3), round(t + C.duration(mp3), 3), seg.get("de") or seg["en"], "de" in seg))
                t += C.duration(mp3) + SEG_GAP
            t += (tight - 0.07) if tight else LINE_GAP - SEG_GAP
        if not tight:
            t += sc.get("hold", 0)
        header = sc.get("header", timeline[-1]["header"] if timeline else None)
        timeline.append({"scene": sc, "start": start, "end": t, "shows": shows, "hides": hides, "header": header})
        if not tight:
            t += sc.get("gap", SCENE_GAP)
    total = t + (0.6 if tight else 0.4)
    return clips, timeline, pops, total, subs


def render(spec_path, out_path):
    global W, H
    spec = json.load(open(spec_path))
    if spec.get("landscape"):                          # long-form: 16:9, road runs left-right
        W, H = 1920, 1080
    clips, timeline, pops, total, subs = plan(spec)
    json.dump({"total": total, "subs": subs, "scenes": [{"start": tl["start"], "header": tl["header"]} for tl in timeline]},
              open(os.path.splitext(out_path)[0] + ".timeline.json", "w"), indent=0)   # for .srt and chapters
    # audio
    tmp = tempfile.mkdtemp()
    inputs, fl = [], []
    for i, (mp3, st) in enumerate(clips):
        inputs += ["-i", mp3]
        d = C.duration(mp3)  # every clip ends on a fade, so no word or room tone stops dead
        fl.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d=0.02,"
                  f"afade=t=out:st={max(0, d - CLIP_FADE)}:d={CLIP_FADE},adelay={int(st * 1000)}:all=1[c{i}]")
    n = len(clips)
    fl.append("".join(f"[c{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total + 4},"
              f"loudnorm=I=-15:TP=-2:LRA=11,apad,atrim=0:{total},asplit=2[voice][key]")  # loudnorm eats its last seconds: pad first
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
    if isinstance(music, list):                 # two seamless loops, switching with a crossfade halfway through
        half, xf = total / 2, 4.0
        inputs += ["-stream_loop", "-1", "-i", music[0], "-stream_loop", "-1", "-i", music[1]]
        fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-13:TP=-1.5:LRA=11,"
                  f"aresample=48000,atrim=0:{half + xf / 2},afade=t=in:d=0.5,afade=t=out:st={half - xf / 2}:d={xf}[ma]")
        fl.append(f"[{k + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-13:TP=-1.5:LRA=11,"
                  f"aresample=48000,atrim=0:{total - half + xf / 2},afade=t=in:d={xf},"
                  f"adelay={int((half - xf / 2) * 1000)}:all=1[mb]")
        fl.append(f"[ma][mb]amix=inputs=2:normalize=0:duration=longest,atrim=0:{total},"
                  f"afade=t=out:st={total - 1.2}:d=1.2,volume={MUSIC_VOL}[m0]")
    else:
        inputs += ["-stream_loop", "-1", "-i", music]
        fl.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-13:TP=-1.5:LRA=11,"
                  f"aresample=48000,atrim=0:{total},afade=t=in:d=0.5,"
                  f"afade=t=out:st={total - 1.2}:d=1.2,volume={MUSIC_VOL}[m0]")
    fl.append("[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[music]")
    mix.append("[music]")
    fl.append("[voice]" + "".join(mix) + f"amix=inputs={1 + len(mix)}:normalize=0,alimiter=limit=0.89,apad[a]")
    wav = os.path.join(tmp, "a.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fl), "-map", "[a]",
                    "-t", f"{total:.3f}", wav], check=True)
    # frames
    road = spec.get("bg") == "road"
    if road:
        use_road_theme()
        import road_loop as RL
        horiz = spec.get("road_dir") == "h"           # default: road runs down the screen, also in 16:9
        if horiz:
            tex = np.ascontiguousarray(np.transpose(RL.strip(H, (W // RL.PERIOD + 1) * RL.PERIOD, tracks=False), (1, 0, 2)))
            loop_px = tex.shape[1] / (RL.SECS * FPS)
        else:
            tex = RL.strip(W, (H // RL.PERIOD + 1) * RL.PERIOD, tracks=H > W)   # 16:9: plain asphalt, no stripes
            loop_px = tex.shape[0] / (RL.SECS * FPS)                  # same drift speed as the approved loop
        badge = shadow(C.icon("pretzel", 150), 14, 120, 6)     # pretzel only, no red square (user)
        yy, xx = np.mgrid[0:H, 0:W]
        vig = (1 - 0.22 * (((xx / W - 0.5) * 2) ** 2 + ((yy / H - 0.5) * 2) ** 2) / 2)[..., None]
    bg = None if road else background()
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
        if road:
            if horiz:
                fr = (np.roll(tex, -int(fi * loop_px) % tex.shape[1], axis=1)[:, :W] * vig).astype(np.uint8)
            else:
                fr = (np.roll(tex, int(fi * loop_px) % tex.shape[0], axis=0)[:H] * vig).astype(np.uint8)
            frame = Image.fromarray(fr).convert("RGBA")
            if W > H:                                   # long-form: pretzel top-left with the part title beside it
                frame.alpha_composite(badge, (60 - 28, 40 - 28))
                hd = header_im(tl["header"])
                if hd is not None:
                    frame.alpha_composite(hd, (240, 115 - hd.height // 2))
            else:
                frame.alpha_composite(badge, ((W - 150) // 2 - 28, 110 - 28))
        else:
            frame = bg.copy()
        local = now - tl["start"]
        L = tl["end"] - tl["start"] + (0 if spec.get("tight") else SCENE_GAP)
        for e in tl["scene"]["els"]:
            if local >= tl["hides"].get(e["id"], 1e9):
                continue
            draw_el(frame, built[si][e["id"]], e, local, tl["shows"].get(e["id"], e.get("at", 0.0) - 0.1), L)
        rgb = frame.convert("RGB")
        if now < 0.5 and not spec.get("tight"):          # fade up from dark (news shorts: graphic pops at 0 s)
            rgb = Image.blend(Image.new("RGB", (W, H)), rgb, now / 0.5)
        if now > total - 0.6:
            rgb = Image.blend(rgb, Image.new("RGB", (W, H)), min(1, (now - total + 0.6) / 0.6))
        ff.stdin.write(rgb.tobytes())
    ff.stdin.close()
    ff.wait()
    return total


if __name__ == "__main__":
    print(render(sys.argv[1], sys.argv[2]))
