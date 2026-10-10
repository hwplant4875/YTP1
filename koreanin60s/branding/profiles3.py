"""Profile picture options (800x800, no text, 뱁새 centered, fits YouTube's circle crop).
Usage: python3 profiles3.py <outdir>; shot.js each profile_<k>.html at 800x800"""
import base64, os, sys
STK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "baepsae")
img = lambda n: "data:image/png;base64," + base64.b64encode(open(f"{STK}/{n}.png", "rb").read()).decode()
def stars(n):
    s, r = "", 11
    for i in range(n):
        r = (r * 9301 + 49297) % 233280; x = r / 233280 * 800
        r = (r * 9301 + 49297) % 233280; y = r / 233280 * 800
        s += f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{3 + i % 3}px;height:{3 + i % 3}px;border-radius:50%;background:#FFF6D8;opacity:{.4 + (i % 4) / 6:.2f}"></div>'
    return s
OPTS = {
    "a": ("radial-gradient(circle at 50% 45%,#FFFBF4 0,#FCE6EA 55%,#F2B8C8 100%)", "", "hi_wave", 600, 95, 110),
    "b": ("radial-gradient(circle at 50% 45%,#F4FBF7 0,#D6F0E4 55%,#A9DCC7 100%)", "", "excited", 620, 90, 100),
    "c": ("radial-gradient(circle at 60% 30%,#454A85 0,transparent 60%),linear-gradient(180deg,#1B1F3B,#2A2E57)", stars(40), "sleeping", 620, 90, 120),
}
for k, (bg, extra, n, w, x, y) in OPTS.items():
    open(f"{sys.argv[1]}/profile_{k}.html", "w").write(f'''<html><head><meta charset="utf-8"><style>body{{margin:0;width:800px;height:800px;overflow:hidden;position:relative;background:{bg}}}
img{{position:absolute;left:{x}px;top:{y}px;width:{w}px;filter:drop-shadow(0 18px 22px rgba(60,40,40,.28))}}</style></head><body>{extra}<img src="{img(n)}"></body></html>''')
