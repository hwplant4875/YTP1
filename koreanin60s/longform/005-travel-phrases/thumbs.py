"""Thumbnails 3a/3b/3c. Usage: python3 thumbs.py <outdir>"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "003-kdrama-phrases", "thumbs"))
from make import STK, render
T = {
"3a": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:60px;top:58px"><span class=chip style="background:#7FA9E8;font-size:40px">✈️ FIRST TRIP TO KOREA</span></div>
<div class="a card" style="left:60px;top:180px;width:780px;height:390px;display:flex;flex-direction:column;align-items:center;justify-content:center">
 <div style="font-size:52px;font-weight:700;color:#8A7A74">How much is this?</div>
 <div style="font-size:104px;font-weight:700;color:#8C6CE0;letter-spacing:-3px;line-height:1.1">이거 얼마예요?</div></div>
<img class=st src="{STK}/suitcase.png" style="left:860px;top:190px;width:390px">""",
"3b": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:56px;top:40px;font-size:190px;font-weight:700;letter-spacing:-6px;line-height:1">40</div>
<div class=a style="left:330px;top:70px;font-size:64px;font-weight:700;line-height:1.05">phrases you'll<br><span style="color:#4F86D6">ACTUALLY</span> use 🇰🇷</div>
<div class=a style="left:60px;top:300px;display:flex;flex-wrap:wrap;gap:20px;width:820px">
 <span class=chip style="background:#5CC4A8;font-size:58px">☕ 아이스 아메리카노</span>
 <span class=chip style="background:#F2C14E;font-size:58px;color:#3A3134">🙋 저기요!</span>
 <span class=chip style="background:#F28BA8;font-size:58px">🙏 감사합니다</span>
 <span class=chip style="background:#A48AEB;font-size:58px">💳 카드 돼요?</span></div>
<img class=st src="{STK}/backpack_bye.png" style="left:900px;top:300px;width:350px">""",
"3c": f"""<div class=bg></div><div class=grid></div>
<div class=a style="left:0;width:1280px;top:44px;text-align:center;font-size:84px;font-weight:700">Don't go to Korea 🇰🇷<br>without these!</div>
<div class="a card" style="left:120px;top:300px;width:560px;height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center">
 <div style="font-size:44px;font-weight:700;color:#8A7A74">Excuse me!</div><div style="font-size:150px;font-weight:700;color:#D99A00;line-height:1.05">저기요!</div></div>
<img class=st src="{STK}/raise_hand.png" style="left:760px;top:250px;width:380px">""",
}
if __name__ == "__main__":
    render(T, sys.argv[1])
