"""Swap burned-in subtitles for Korean ones.

Two steps, with a human/LLM translation pass in between:

  python3 subswap.py detect in.mp4 subs.json
      OCR every few frames, find the burned-in subtitle lines and their exact
      boxes, group them into timed segments. Fill each segment's "ko" field.

  python3 subswap.py render in.mp4 subs.json out.mp4
      Blur only the pixels under the original subtitle boxes (rounded,
      feathered, frame-accurate), then draw the Korean line on the same spot
      with stroke and shadow (libass). No black boxes.

Only use on videos you have permission to translate.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")


def ffmpeg_bin():
    for p in ("ffmpeg",):
        if subprocess.run(["which", p], capture_output=True).returncode == 0:
            return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def norm(t):
    return re.sub(r"[^a-z0-9äöüß]+", " ", t.lower()).strip()


def latin_ratio(t):
    letters = [c for c in t if c.isalpha()]
    if not letters:
        return 0
    return sum(c.isascii() or c in "äöüßÄÖÜ" for c in letters) / len(letters)


# ---------------------------------------------------------------- detect

def merge_rows(boxes):
    """OCR often splits one subtitle line into words; join boxes on the same row."""
    rows = []
    for b in sorted(boxes, key=lambda b: (b["box"][1] + b["box"][3]) / 2):
        cy = (b["box"][1] + b["box"][3]) / 2
        row = rows[-1] if rows else None
        if row and abs(cy - row["cy"]) < (row["box"][3] - row["box"][1]) * 0.5:
            row["parts"].append(b)
            x0, y0, x1, y1 = row["box"]
            bx0, by0, bx1, by1 = b["box"]
            row["box"] = [min(x0, bx0), min(y0, by0), max(x1, bx1), max(y1, by1)]
        else:
            rows.append({"cy": cy, "box": list(b["box"]), "parts": [b]})
    out = []
    for r in rows:
        parts = sorted(r["parts"], key=lambda p: p["box"][0])
        out.append({"box": r["box"], "text": " ".join(p["text"] for p in parts),
                    "conf": min(p["conf"] for p in parts)})
    return out


def detect(src, out, step, y_min, y_max, min_conf):
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    samples = []  # (frame_idx, [ {box, text} ])
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % step == 0:
            res, _ = ocr(frame)
            lines = []
            for pts, text, conf in res or []:
                conf = float(conf)
                pts = np.array(pts, dtype=float)
                x0, y0 = pts.min(0)
                x1, y1 = pts.max(0)
                cy = (y0 + y1) / 2 / H
                if conf < min_conf or not (y_min <= cy <= y_max):
                    continue
                if latin_ratio(text) < 0.8 or len(norm(text)) < 2:
                    continue
                lines.append({"box": [int(x0), int(y0), int(x1), int(y1)],
                              "text": text.strip(), "conf": round(conf, 3)})
            samples.append((i, merge_rows(lines)))
            print(f"\r{i}/{n}", end="", file=sys.stderr)
        i += 1
    print(file=sys.stderr)

    # group consecutive samples that show the same caption
    segs = []
    for fi, lines in samples:
        if not lines:
            continue
        text = " ".join(l["text"] for l in lines)
        last = segs[-1] if segs else None
        same = (last and fi - last["f1"] <= step * 3 and
                difflib.SequenceMatcher(None, norm(text), norm(last["text"])).ratio() > 0.75)
        if same:
            last["f1"] = fi
            last["frames"][fi] = [l["box"] for l in lines]
            if len(text) > len(last["text"]):
                last["text"] = text  # keep the fullest read (typewriter captions grow)
                last["lines"] = [l["text"] for l in lines]
        else:
            segs.append({"f0": fi, "f1": fi, "text": text,
                         "lines": [l["text"] for l in lines],
                         "frames": {fi: [l["box"] for l in lines]}})

    out_segs = []
    for k, s in enumerate(segs):
        boxes = [b for bs in s["frames"].values() for b in bs]
        union = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                 max(b[2] for b in boxes), max(b[3] for b in boxes)]
        out_segs.append({
            "id": k + 1,
            "start": round(s["f0"] / fps, 3),
            "end": round((s["f1"] + step) / fps, 3),
            "f0": s["f0"], "f1": min(s["f1"] + step - 1, n - 1),
            "text": s["text"], "lines": s["lines"],
            "box": union,
            "line_h": int(np.median([b[3] - b[1] for b in boxes])),
            "frames": {str(f): b for f, b in s["frames"].items()},
            "ko": "",
        })
    json.dump({"src": os.path.basename(src), "fps": fps, "w": W, "h": H,
               "frames": n, "step": step, "segments": out_segs},
              open(out, "w"), ensure_ascii=False, indent=1)
    print(f"{len(out_segs)} segments -> {out}")


# ---------------------------------------------------------------- render

def boxes_at(seg, f, step):
    """Boxes for frame f: nearest sampled frame inside the segment."""
    keys = sorted(int(k) for k in seg["frames"])
    near = min(keys, key=lambda k: abs(k - f))
    return seg["frames"][str(near)]


def mask_frame(W, H, boxes, pad, radius, feather):
    m = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in boxes:
        x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
        r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
        cv2.rectangle(m, (x0 + r, y0), (x1 - r, y1), 255, -1)
        cv2.rectangle(m, (x0, y0 + r), (x1, y1 - r), 255, -1)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
            cv2.circle(m, (cx, cy), r, 255, -1)
    if feather:
        k = feather * 2 + 1
        m = cv2.GaussianBlur(m, (k, k), feather / 2)
    return m


def ass_color(hexrgb, alpha=0):
    r, g, b = hexrgb[0:2], hexrgb[2:4], hexrgb[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def text_width(font_path, size, text):
    from PIL import ImageFont
    f = ImageFont.truetype(font_path, size)
    return max(f.getlength(t) for t in text.split("\n"))


def ass_time(t):
    t = max(t, 0)
    h, t = divmod(t, 3600)
    m, s = divmod(t, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def build_ass(data, path, font_file, font_name, accent, scale):
    W, H = data["w"], data["h"]
    outline = max(3, round(W / 1080 * 7))
    shadow = max(2, round(W / 1080 * 5))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KO,{font_name},80,&H00FFFFFF,&H00FFFFFF,&H00141414,&H8C000000,0,0,0,0,100,100,0,0,1,{outline},{shadow},5,40,40,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for s in data["segments"]:
        ko = (s.get("ko") or "").strip()
        if not ko:
            continue
        x0, y0, x1, y1 = s["box"]
        n_lines = ko.count("\n") + 1
        # cover the original: line height at least the original's, width fits the frame
        size = int(max(s["line_h"] * 1.25, W * 0.055) * scale)
        plain = re.sub(r"\*", "", ko)
        while size > 30 and text_width(font_file, size, plain) > W * 0.9:
            size -= 2
        cx = (x0 + x1) // 2
        cx = min(max(cx, W // 2 - W // 4), W // 2 + W // 4)
        cy = (y0 + y1) // 2
        body = ko.replace("\n", "\\N")
        body = re.sub(r"\*(.+?)\*", lambda m: "{\\c" + ass_color(accent) + "&}" + m.group(1) + "{\\c&HFFFFFF&}", body)
        pop = "{\\fscx88\\fscy88\\t(0,90,\\fscx104\\fscy104)\\t(90,160,\\fscx100\\fscy100)}"
        ev.append(f"Dialogue: 0,{ass_time(s['start'])},{ass_time(s['end'])},KO,,0,0,0,,"
                  f"{{\\pos({cx},{cy})\\fs{size}}}{pop}{body}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def erase(frame, boxes, soft_mask, blur):
    """Wipe the glyph strokes first (inpaint), then blur, so no ghost letters show through."""
    H, W = frame.shape[:2]
    work = frame.copy()
    for x0, y0, x1, y1 in boxes:
        m = max(8, (y1 - y0) // 3)
        X0, Y0, X1, Y1 = max(0, x0 - m), max(0, y0 - m), min(W, x1 + m), min(H, y1 + m)
        crop = work[Y0:Y1, X0:X1]
        g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(g, 60, 160)
        k = max(3, (y1 - y0) // 10) | 1
        strokes = cv2.dilate(edges, np.ones((k, k), np.uint8), iterations=2)
        strokes = cv2.morphologyEx(strokes, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
        work[Y0:Y1, X0:X1] = cv2.inpaint(crop, strokes, 5, cv2.INPAINT_TELEA)
    k = int(blur * 3) | 1
    blurred = cv2.GaussianBlur(work, (k, k), blur)
    a = (soft_mask.astype(np.float32) / 255)[..., None]
    return (frame * (1 - a) + blurred * a).astype(np.uint8)


def render(src, subs, out, blur, pad, radius, feather, font, accent, scale, keep_tmp):
    data = json.load(open(subs))
    W, H, fps, n = data["w"], data["h"], data["fps"], data["frames"]
    font_file = os.path.join(FONTS, font)
    from PIL import ImageFont
    font_name = ImageFont.truetype(font_file, 10).getname()[0]
    ass_path = os.path.splitext(out)[0] + ".ass"
    build_ass(data, ass_path, font_file, font_name, accent, scale)

    by_frame = {}
    for s in data["segments"]:
        for f in range(s["f0"], s["f1"] + 1):
            by_frame.setdefault(f, []).extend(boxes_at(s, f, data["step"]))

    ff = ffmpeg_bin()
    esc = lambda p: p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    cmd = [ff, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-i", src,
           "-vf", f"ass='{esc(ass_path)}':fontsdir='{esc(FONTS)}'",
           "-map", "0:v", "-map", "1:a?",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cap = cv2.VideoCapture(src)
    f = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        boxes = by_frame.get(f)
        if boxes:
            frame = erase(frame, boxes, mask_frame(W, H, boxes, pad, radius, feather), blur)
        p.stdin.write(frame.tobytes())
        f += 1
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg failed")
    if not keep_tmp:
        os.remove(ass_path)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect")
    d.add_argument("src"); d.add_argument("out")
    d.add_argument("--step", type=int, default=2, help="OCR every N frames")
    d.add_argument("--y-min", type=float, default=0.12, help="ignore text above this (fraction of height)")
    d.add_argument("--y-max", type=float, default=0.90, help="ignore text below this (UI zone)")
    d.add_argument("--min-conf", type=float, default=0.6)
    r = sub.add_parser("render")
    r.add_argument("src"); r.add_argument("subs"); r.add_argument("out")
    r.add_argument("--blur", type=float, default=18)
    r.add_argument("--pad", type=int, default=10)
    r.add_argument("--radius", type=int, default=18)
    r.add_argument("--feather", type=int, default=6)
    r.add_argument("--font", default="Pretendard-Black.otf")
    r.add_argument("--accent", default="FFD400", help="RGB hex for *highlighted* words")
    r.add_argument("--scale", type=float, default=1.0)
    r.add_argument("--keep-ass", action="store_true")
    a = ap.parse_args()
    if a.cmd == "detect":
        detect(a.src, a.out, a.step, a.y_min, a.y_max, a.min_conf)
    else:
        render(a.src, a.subs, a.out, a.blur, a.pad, a.radius, a.feather, a.font, a.accent, a.scale, a.keep_ass)


if __name__ == "__main__":
    main()
