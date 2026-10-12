"""Hallyu news shorts 011-013 with ORIGINAL source visuals (article screenshots, official stills/thumbnails).
Images are not in the repo (third-party); pass the folder that holds them: python3 build_specs.py <img dir> <out dir>.
Writes <out>/<name>/spec.json with images inlined as data URIs (engine.py renders them in white boxes)."""
import base64, json, os, sys
from PIL import Image
IMG, OUT = sys.argv[1], sys.argv[2]
def uri(n, crop=None):
    p = f"{IMG}/{n}.jpg"
    if crop:
        im = Image.open(p).convert("RGB").crop(crop); p = f"{OUT}/_{n}_c.jpg"; os.makedirs(OUT, exist_ok=True); im.save(p, quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()
def pic(n, y, at, w=960, cap=None, crop=None, anim="up", x=None):
    h = f"<img src='{uri(n, crop)}' style='width:100%;display:block;border-radius:18px'>"
    if cap: h += f"<div style='font-family:Pretendard,sans-serif;font-weight:700;font-size:32px;color:#6b5b55;margin-top:10px;white-space:nowrap'>{cap}</div>"
    e = {"type": "box", "html": h, "w": w, "y": y, "at": at, "anim": anim, "style": "padding:12px"}
    if x is not None: e["x"] = x
    return e
def L(k, say, pose, gap=None, ko=False):
    d = {"k": k, "say": say, "pose": pose}
    if gap: d["gap"] = gap
    if ko: d["lang"] = "ko"
    return d
def chip(html, y, at, c="p", size=None):
    e = {"type": "chip", "html": html, "c": c, "y": y, "at": at}
    if size: e["size"] = size
    return e
def word(ko, rom, en, c, y, at, size=150, w=700, x=None):
    e = {"type": "word", "ko": ko, "rom": rom, "en": en, "c": c, "size": size, "w": w, "y": y, "at": at}
    if x is not None: e["x"] = x
    return e
def box(html, y, at, fs=46, w=900): return {"type": "box", "html": f"<div class='txt' style='font-size:{fs}px;white-space:nowrap;line-height:1.4'>{html}</div>", "w": w, "pad": 22, "y": y, "at": at, "anim": "up"}
def end(q): return {"from": "e0", "els": [
    {"type": "txt", "html": "Korean in <span class='c-p'>60s</span>", "size": 110, "y": 640, "at": "e0", "style": "font-family:YouTube Sans,Pretendard;font-weight:900"},
    {"type": "box", "html": f"<div class='txt' style='font-size:46px;white-space:nowrap'>{q}</div>", "w": 960, "pad": 22, "y": 830, "at": "e0+0.7", "anim": "up"}]}
S = {}
def big(html, y, at, fs=58, w=980):
    return {"type": "txt", "html": html, "size": fs, "w": w, "y": y, "at": at, "style": "font-family:YouTube Sans,Pretendard;font-weight:900;line-height:1.2"}
# News shorts carry no Korean lesson (user 2026-10-12): just the story, packed with detail, a new visual every few seconds.
S["011-kpdh2-theaters"] = {"label": "K-NEWS 📣", "labelColor": "#E25B5B", "pose0": "clap_confetti", "lines": [
    L("h1", "Big news! KPop Demon Hunters 2 is coming to theaters!", "clap_confetti"),
    L("a1", "Netflix co-CEO Ted Sarandos revealed it at Bloomberg's Screentime event.", "talk"),
    L("a2", "He said, when the sequel comes, you can expect a very broad theatrical release.", "excited"),
    L("a3", "That's huge, because the first movie skipped theaters and went straight to Netflix.", "shocked"),
    L("a4", "Then it became the first Netflix title ever to pass three hundred million views.", "mind_blown"),
    L("a5", "And when a sing-along version hit theaters for one weekend, it was number one at the U.S. box office.", "clap_confetti"),
    L("a6", "Netflix and Sony confirmed the sequel in March, with directors Maggie Kang and Chris Appelhans coming back.", "point_idea"),
    L("a7", "It's reportedly aiming for twenty twenty-nine, but there's no release date yet.", "thinking"),
    L("e0", "Would you watch it in theaters? Comment below!", "love_heart")],  # e0 has no gap: read with the lines before it (alone, v3 sounded muffled)
  "scenes": [
    {"els": [pic("art_pinkh", 400, "h1", cap="PinkNews · Oct 1, 2026"), pic("huntrix_v", 900, "h1+1.4", w=860, cap="HUNTR/X · KPop Demon Hunters (Netflix)")]},
    {"from": "a1", "els": [pic("sarandos", 560, "a1", cap="Ted Sarandos (Netflix co-CEO) · Bloomberg Screentime"), chip("🎤 Oct 1, 2026", 1000, "a1+1.0", "y")]},
    {"from": "a2", "els": [pic("art_cbm_quote", 420, "a2", cap="ComicBookMovie · Oct 2, 2026"), big("“You can expect a<br><span class='c-p'>very broad</span> theatrical release.”", 820, "a2+1.2")]},
    {"from": "a3", "els": [pic("huntrix_sing", 560, "a3", cap="KPop Demon Hunters (Netflix, June 2025)"), chip("📺 Netflix only · no theaters", 1000, "a3+1.6", "b")]},
    {"from": "a4", "els": [pic("art_jad", 330, "a4", cap="Korea JoongAng Daily"), pic("netflix_top", 800, "a4+1.0", w=900, cap="Netflix · Most popular movies, all time")]},
    {"from": "a5", "els": [pic("singalong", 560, "a5", cap="Sing-along screening · Aug 2025"), chip("🍿 #1 at the U.S. box office", 1010, "a5+2.6", "p")]},
    {"from": "a6", "els": [pic("art_variety", 330, "a6", cap="Variety · Mar 2026"), pic("directors", 820, "a6+2.4", w=860, cap="Maggie Kang & Chris Appelhans · Netflix Tudum")]},
    {"from": "a7", "els": [pic("huntrix_close", 560, "a7", cap="KPop Demon Hunters (Netflix)"), chip("🎯 2029? · date not announced", 1000, "a7+1.6", "y")]},
    end("In theaters? 🍿👇")]}
S["012-jinu-voice-chef"] = {"label": "K-NEWS 📣", "labelColor": "#E25B5B", "pose0": "shocked", "lines": [
    L("h1", "Jinu's voice is back, and this time he's a chef!", "shocked"),
    L("b1", "안효섭, the voice of Jinu in KPop Demon Hunters, stars in the new JTBC drama, Final Table.", "talk"),
    L("b2", "He plays Kang Han, a genius chef known as Chris K, who moves to a new restaurant every year.", "excited"),
    L("b3", "Back in Korea, he becomes head chef of Familia, an Italian restaurant about to close.", "nervous_sweat"),
    L("b4", "To save it, he teams up with hall manager 최송이, played by 홍화연.", "point_idea"),
    L("b5", "Together they enter The Table, K Chef twenty twenty-six, a contest for the best Korean chef.", "clap_confetti"),
    L("b6", "And his old rival, chef 차우진, played by 장률, is waiting.", "steam_angry"),
    L("b7", "To prepare, 안효섭 trained so hard with knives that he badly cut his finger.", "shocked"),
    L("b8", "Final Table starts October twenty-fourth on JTBC.", "excited"),
    L("e0", "Will you watch it? Comment below!", "finger_heart", .45)],
  "scenes": [
    {"els": [pic("jinu_red", 420, "h1", w=860, cap="Jinu · KPop Demon Hunters (Netflix)"), pic("ft_teaser1", 960, "h1+1.6", w=860, cap="JTBC 〈파이널 테이블〉 teaser")]},
    {"from": "b1", "els": [pic("ahn_photo", 520, "b1", w=580, crop=(0, 40, 700, 680), cap="안효섭 Ahn Hyo-seop"), pic("art_wt3h2", 1040, "b1+2.2", w=900, cap="Wikitree")]},
    {"from": "b2", "els": [pic("ft_poster2", 600, "b2", w=520, cap="〈파이널 테이블〉 poster · JTBC"), chip("👨‍🍳 Kang Han a.k.a. Chris K", 1060, "b2+1.4", "y")]},
    {"from": "b3", "els": [pic("ft_apron", 470, "b3", cap="〈파이널 테이블〉 teaser · JTBC"), pic("art_wt4h", 960, "b3+1.8", w=920, cap="Wikitree · Oct 4, 2026")]},
    {"from": "b4", "els": [pic("ft_teaser2", 560, "b4", cap="Kang Han & Choi Song-yi · 2nd teaser"), chip("🤝 홍화연 Hong Hwa-yeon", 1000, "b4+2.0", "p")]},
    {"from": "b5", "els": [pic("ft_teaser3", 560, "b5", cap="〈파이널 테이블〉 3rd teaser · JTBC"), chip("🏆 The Table: K Chef 2026", 1000, "b5+1.2", "y"),
                           chip("⚔️ Rival chef: 장률 Jang Ryul", 1110, "b6", "b", 44)]},
    {"from": "b7", "els": [pic("art_wt1h", 500, "b7", cap="Wikitree · Oct 9, 2026"), big("🔪 Cut his finger<br>in knife training", 880, "b7+1.4", 64)]},
    {"from": "b8", "els": [pic("ft_poster", 540, "b8", w=860, cap="〈파이널 테이블〉 poster · JTBC"), chip("📺 Oct 24 · JTBC", 960, "b8+1.0", "y"), chip("Disney+ 🇰🇷 · Prime Video 🌍", 1070, "b8+1.8", "b", 44)]},
    end("Will you watch it? 👇")]}
S["013-kpdh-korean-words"] = {"label": "KPDH KOREAN 🐯", "labelColor": "#8C6CE0", "pose0": "popcorn_tv", "lines": [
    L("h1", "KPop Demon Hunters is full of hidden Korean words. Did you catch these?", "popcorn_tv"),
    L("w1", "The magic barrier, the Honmoon, comes from", "talk", .4), L("w1k", "혼문.", "mind_blown", ko=True),
    L("w1e", "Soul, plus gate. A soul gate!", "point_idea"),
    L("w2", "And the Saja Boys? They're named after", "nervous_sweat", .4), L("w2k", "저승사자.", "shocked", ko=True),
    L("w2e", "The grim reaper!", "nervous_sweat"),
    L("w3", "The tiger is", "excited", .4), L("w3k", "호랑이,", "clap_confetti", ko=True),
    L("w4", "and the bird is a magpie,", "talk"), L("w4k", "까치.", "laugh_flap", ko=True),
    L("w4e", "A classic pair from old Korean folk paintings!", "thumbs_up"),
    L("e0", "Which one did you know? Comment below!", "love_heart", .45)],
  "scenes": [
    {"els": [pic("honmoon_stage", 560, "h1", cap="KPop Demon Hunters (Netflix)"), {"type": "txt", "html": "Hidden <span class='c-k'>Korean</span> in<br>KPop Demon Hunters", "size": 68, "y": 1060, "at": "h1+0.6",
             "style": "font-family:YouTube Sans,Pretendard;font-weight:900;line-height:1.15;white-space:nowrap"}]},
    {"from": "w1", "els": [pic("golden_mv", 450, "w1", cap="'Golden' music video · Netflix"), word("혼문", "hon-mun", "Honmoon", "k", 925, "w1k", 140), box("혼 soul + 문 gate = soul gate 🚪", 1135, "w1e", 46, 860)]},
    {"from": "w2", "els": [pic("jinu_gat", 450, "w2", cap="Saja Boys in 갓 hats · Netflix"), word("저승사자", "jeo-seung-sa-ja", "grim reaper", "b", 925, "w2k", 130, 760), box("black hanbok + 갓 = Korean grim reaper 🖤", 1135, "w2e", 40, 900)]},
    {"from": "w3", "els": [pic("hojakdo", 500, "w3", w=560, crop=(0, 0, 700, 700), cap="호작도 · Korean folk painting"),
                           word("호랑이", "ho-rang-i", "tiger", "y", 1040, "w3k", 110, 450, 290), word("까치", "kka-chi", "magpie", "b", 1040, "w4k", 120, 450, 790)]},
    end("Which one did you know? 👇")]}
for k, v in S.items():
    os.makedirs(f"{OUT}/{k}", exist_ok=True); json.dump(v, open(f"{OUT}/{k}/spec.json", "w"), ensure_ascii=False)
print("ok")
