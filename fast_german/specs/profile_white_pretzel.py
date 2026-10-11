"""Profile (user 2026-10-11): plain white background, pretzel with a stroke. A: dark brown outline. B: white sticker
edge with a soft shadow so it still reads on white."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from PIL import Image, ImageDraw, ImageFilter
import common as C
from profile_night_pretzel import fill_all_holes
D = "/mnt/project-files/fast_german/branding/final/"
S = 800


def stroke_mask(p, grow, fill=True):
    a = p.split()[3].filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(grow))
    a = a.filter(ImageFilter.GaussianBlur(4)).point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.GaussianBlur(1))
    return fill_all_holes(a) if fill else a


def profile(kind):
    raw = C.icon("pretzel", 560)
    p = Image.new("RGBA", (raw.width + 80, raw.height + 80)); p.alpha_composite(raw, (40, 40))
    im = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    pos = ((S - p.width) // 2, (S - p.height) // 2 + 6)
    if kind == "A":
        m = stroke_mask(p, 25, fill=False)     # outline also runs round the inner holes
        st = Image.new("RGBA", p.size, (92, 52, 24, 0)); st.putalpha(m)
    else:
        m = stroke_mask(p, 41)
        sh = Image.new("RGBA", p.size, (0, 0, 0, 0)); sh.putalpha(m.point(lambda v: v * 70 // 255))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (pos[0], pos[1] + 12))
        st = Image.new("RGBA", p.size, (255, 255, 255, 0)); st.putalpha(m)
    st.alpha_composite(p)
    im.alpha_composite(st, pos)
    return im


if __name__ == "__main__":
    A, B = profile("A"), profile("B")
    A.convert("RGB").save(D + "profile_white_A_outline.png"); B.convert("RGB").save(D + "profile_white_B_sticker.png")
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    sheet = Image.new("RGB", (760, 230), (30, 30, 30))
    for i, im in enumerate((A, B)):
        for s, (x, y) in ((176, (20, 20)), (88, (220, 20)), (40, (220, 130))):
            sheet.paste(im.convert("RGB").resize((s, s), Image.LANCZOS), (x + i * 380, y), m.resize((s, s)))
    sheet.save(D + "profile_white_sizes.png")
