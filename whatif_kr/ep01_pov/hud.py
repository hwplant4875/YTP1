# Glass HUD in the AFTER THE DOOR layout, Korean labels.
# python3 hud.py <in.png> <out.jpg> <step> "<subtitle>" [card.png "card title" "card line"]
import sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD = "/home/user/YTP1/whatif_kr/ep01_pov/fonts/"
def F(w, s): return ImageFont.truetype(FD + f"Pretendard-{w}.otf", s)

def kor_big(x, unit):
    for v, u in ((1e16, "경"), (1e12, "조"), (1e8, "억"), (1e4, "만")):
        if x >= v:
            q = x / v
            return (f"{q:,.0f}" if q >= 100 else f"{q:.1f}".rstrip("0").rstrip(".")) + f"{u} {unit}"
    return f"{x:,.0f} {unit}" if x >= 10 else f"{x:.1f}".rstrip("0").rstrip(".") + f" {unit}"

def height(n):
    m = 1.75 * 2 ** n
    if m < 10: return f"{m:.1f}", "m"
    if m < 1000: return f"{m:,.0f}", "m"
    km = m / 1000
    return (f"{km:.1f}" if km < 100 else f"{km:,.0f}"), "km"

def weight(n):
    kg = 70 * 8 ** n
    if kg < 1000: return f"몸무게 {kg:,.0f} kg"
    return "몸무게 " + kor_big(kg / 1000, "톤")

def tnt(n):
    g = {0: 0.1, 1: 0.7}.get(n, 180 * 16 ** (n - 3))
    if g < 1000: return f"≈ TNT {g:.1f} g" if g < 10 else f"≈ TNT {g:,.0f} g"
    if g < 1e6: return f"≈ TNT {g / 1000:.1f} kg" if g < 1e4 else f"≈ TNT {g / 1000:,.0f} kg"
    return "≈ TNT " + kor_big(g / 1e6, "톤")

def glass(im, box, r=22, tint=(255, 255, 255), a=46):
    x0, y0, x1, y1 = box
    reg = im.crop(box).filter(ImageFilter.GaussianBlur(18))
    ov = Image.new("RGB", reg.size, tint); reg = Image.blend(reg, ov, a / 255)
    mask = Image.new("L", reg.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, reg.size[0] - 1, reg.size[1] - 1], r, fill=255)
    im.paste(reg, (x0, y0), mask)
    d = ImageDraw.Draw(im, "RGBA"); d.rounded_rectangle(box, r, outline=(255, 255, 255, 90), width=2)
    # soft drop shadow line under the panel
    return d

def shadow_text(im, xy, s, font, fill=(255, 255, 255), anchor="la"):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((xy[0] + 1, xy[1] + 2), s, font=font, fill=(0, 0, 0, 120), anchor=anchor)
    im.paste(sh.filter(ImageFilter.GaussianBlur(3)), (0, 0), sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(im).text(xy, s, font=font, fill=fill, anchor=anchor)

def hud(src, out, n, sub, card=None, ctitle="", cline=""):
    im = Image.open(src).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    M = -1.7 + 0.8 * n
    # top-left: earthquake
    glass(im, (56, 56, 476, 210))
    shadow_text(im, (86, 82), f"STEP {n}  ·  지진 규모", F("SemiBold", 19))
    shadow_text(im, (80, 108), f"M {M:.1f}".replace("-", "−"), F("Light", 76))
    shadow_text(im, (86, 184), tnt(n), F("Regular", 19))
    # top-right: height
    glass(im, (1394, 56, 1864, 264))
    shadow_text(im, (1834, 82), "현재 키", F("SemiBold", 19), anchor="ra")
    v, u = height(n)
    fu = F("Light", 40); fv = F("Light", 84)
    uw = ImageDraw.Draw(im).textlength(u, font=fu)
    shadow_text(im, (1834 - uw - 8, 196), v, fv, anchor="rs"); shadow_text(im, (1834, 196), u, fu, anchor="rs")
    shadow_text(im, (1834, 206), weight(n), F("Regular", 21), anchor="ra")
    d = ImageDraw.Draw(im, "RGBA")
    d.line([(1424, 236), (1834, 236)], fill=(255, 255, 255, 110), width=2)
    frac = min(1, n / 25); d.line([(1424, 236), (1424 + 410 * frac, 236)], fill=(255, 214, 92, 255), width=4)
    d.ellipse([1424 + 410 * frac - 5, 231, 1424 + 410 * frac + 5, 241], fill=(255, 238, 180, 255))
    shadow_text(im, (1424, 244), "1.75 m", F("Regular", 13)); shadow_text(im, (1834, 244), "58,720 km", F("Regular", 13), anchor="ra")
    # bottom-left: seismograph
    glass(im, (56, 840, 456, 962))
    shadow_text(im, (80, 860), "지진계", F("SemiBold", 17)); shadow_text(im, (432, 860), f"스케일 ×10^{max(0, n)}", F("Regular", 15), anchor="ra")
    rnd = random.Random(n); pts = []
    for i in range(160):
        x = 80 + i * 2.2; amp = 4 + 22 * math.exp(-((i - 110) / 18) ** 2) * min(1, (M + 2) / 6)
        pts.append((x, 918 + rnd.uniform(-1, 1) * amp))
    d.line(pts, fill=(255, 255, 255, 230), width=2); d.ellipse([428, 914, 436, 922], fill=(255, 255, 255, 255))
    # subtitle pill
    fs = F("Medium", 38); lines = sub.split("\n")
    wmax = max(ImageDraw.Draw(im).textlength(l, font=fs) for l in lines)
    h = 30 + 48 * len(lines); y1 = 1018; y0 = y1 - h; x0 = 960 - wmax / 2 - 38; x1 = 960 + wmax / 2 + 38
    glass(im, (int(x0), int(y0), int(x1), int(y1)), r=26, tint=(40, 46, 56), a=70)
    for k, l in enumerate(lines): shadow_text(im, (960, y0 + 15 + 48 * k), l, fs, anchor="ma")
    # comparison card (real photo goes here)
    if card:
        ph = Image.open(card).convert("RGB"); ph = ph.resize((430, int(430 * ph.size[1] / ph.size[0])))
        ph = ph.crop((0, 0, 430, min(ph.size[1], 420)))
        y0 = 290; y1 = y0 + 20 + ph.size[1] + 130
        glass(im, (1394, y0, 1864, y1))
        mk = Image.new("L", ph.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, ph.size[0] - 1, ph.size[1] - 1], 16, fill=255)
        im.paste(ph, (1414, y0 + 20), mk)
        ty = y0 + 20 + ph.size[1] + 22
        shadow_text(im, (1416, ty), ctitle, F("SemiBold", 34)); shadow_text(im, (1416, ty + 48), cline, F("Regular", 22))
    im.save(out, quality=92)

if __name__ == "__main__":
    a = sys.argv
    hud(a[1], a[2], int(a[3]), a[4].replace("\\n", "\n"), *(a[5:8] if len(a) > 5 else []))
