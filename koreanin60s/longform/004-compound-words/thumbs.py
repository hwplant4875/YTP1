"""Thumbnails 2a/2b/2c. Usage: python3 thumbs.py <outdir>"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "003-kdrama-phrases", "thumbs"))
from make import STK, render
def tile(e, ko, en, bg="#fff", fs=150):
    return f'<div class="card" style="display:inline-flex;flex-direction:column;align-items:center;padding:18px 34px 16px;background:{bg}"><div style="font-size:{fs*0.6:.0f}px;line-height:1">{e}</div><div style="font-size:{fs}px;font-weight:700;line-height:1.05">{ko}</div><div style="font-size:{fs*0.3:.0f}px;font-weight:700;color:#8A7A74">{en}</div></div>'
OP = '<span style="font-size:110px;font-weight:700;color:#C9B8AC;margin:0 18px">{}</span>'
T = {
"2a": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:0;width:1280px;top:60px;display:flex;align-items:center;justify-content:center">{tile("👁️","눈","eye")}{OP.format("+")}{tile("💧","물","water")}{OP.format("=")}<div class="card" style="width:250px;height:330px;display:flex;align-items:center;justify-content:center;font-size:200px;font-weight:700;color:#5CC4A8">?</div></div>
<div class=a style="left:60px;top:510px;font-size:84px;font-weight:700;line-height:1">Can you guess it? 🧩</div>
<img class=st src="{STK}/point_idea.png" style="left:960px;top:400px;width:300px">""",
"2b": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:60px;top:50px;font-size:120px;font-weight:700;line-height:1;letter-spacing:-3px">Korean is<br><span style="color:#E2A21C">LEGO</span> 🧩</div>
<div class=a style="left:60px;top:330px;display:flex;align-items:center">{tile("💧","물","water",fs=110)}{OP.format("+")}{tile("🥩","고기","meat",fs=110)}{OP.format("=")}{tile("🐟","물고기","fish",fs=110,bg="#FFF4D6")}</div>
<img class=st src="{STK}/mind_blown.png" style="left:960px;top:20px;width:290px">""",
"2c": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:0;width:1280px;top:40px;text-align:center;font-size:84px;font-weight:700">Hand + Neck = Wrist?! 🤯</div>
<div class=a style="left:0;width:1280px;top:190px;display:flex;align-items:center;justify-content:center">{tile("✋","손","hand")}{OP.format("+")}{tile("🦒","목","neck")}{OP.format("=")}{tile("⌚","손목","wrist",bg="#E3F5EE")}</div>
<img class=st src="{STK}/shocked.png" style="left:1060px;top:490px;width:210px">""",
}
if __name__ == "__main__":
    render(T, sys.argv[1])
