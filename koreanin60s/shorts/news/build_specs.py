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
def chip(html, y, at, c="p"): return {"type": "chip", "html": html, "c": c, "y": y, "at": at}
def word(ko, rom, en, c, y, at, size=150, w=700, x=None):
    e = {"type": "word", "ko": ko, "rom": rom, "en": en, "c": c, "size": size, "w": w, "y": y, "at": at}
    if x is not None: e["x"] = x
    return e
def box(html, y, at, fs=46, w=900): return {"type": "box", "html": f"<div class='txt' style='font-size:{fs}px;white-space:nowrap;line-height:1.4'>{html}</div>", "w": w, "pad": 22, "y": y, "at": at, "anim": "up"}
def end(q): return {"from": "e0", "els": [
    {"type": "txt", "html": "Korean in <span class='c-p'>60s</span>", "size": 110, "y": 640, "at": "e0", "style": "font-family:YouTube Sans,Pretendard;font-weight:900"},
    {"type": "box", "html": f"<div class='txt' style='font-size:46px;white-space:nowrap'>{q}</div>", "w": 960, "pad": 22, "y": 830, "at": "e0+0.7", "anim": "up"}]}
S = {}
S["011-kpdh2-theaters"] = {"label": "K-NEWS 📣", "labelColor": "#E25B5B", "pose0": "clap_confetti", "lines": [
    L("h1", "Big news! KPop Demon Hunters 2 is coming to theaters!", "clap_confetti"),
    L("n1", "Netflix's boss says the sequel gets a big, worldwide release in the", "talk", .4), L("n1k", "극장.", "popcorn_tv", ko=True),
    L("n2", "The theater! It's aiming for twenty twenty-nine, and the original directors are coming back.", "excited"),
    L("t0", "So here's your word for the sequel:", "point_idea", .45), L("t0k", "속편.", "mind_blown", ko=True),
    L("t1", "Sequel. Part two!", "thumbs_up"),
    L("e0", "Will you watch it in theaters? Comment below!", "love_heart", .45)],
  "scenes": [
    {"els": [pic("art_pink", 640, "h1", cap="PinkNews · Oct 1, 2026"), {"type": "stamp", "html": "BIG NEWS 📣", "c": "p", "size": 86, "y": 1140, "at": "h1@end-0.8", "anim": "stamp"}]},
    {"from": "n1", "els": [pic("sarandos", 500, "n1", cap="Ted Sarandos (Netflix co-CEO) · Bloomberg"), word("극장", "geuk-jang", "movie theater", "p", 1060, "n1k", 140)]},
    {"from": "n2", "els": [pic("art_cbm", 600, "n2", cap="ComicBookMovie · Oct 2, 2026"), chip("🎯 2029 · same directors", 1130, "n2+2.2", "y")]},
    {"from": "t0", "els": [pic("huntrix_pink", 520, "t0", cap="HUNTR/X · KPop Demon Hunters (Netflix)"), word("속편", "sok-pyeon", "sequel", "k", 1040, "t0k", 150)]},
    end("In theaters? 🍿👇")]}
S["012-jinu-voice-chef"] = {"label": "K-NEWS 📣", "labelColor": "#E25B5B", "pose0": "shocked", "lines": [
    L("h1", "Remember Jinu's voice from KPop Demon Hunters? He's starring in a new K-drama!", "shocked"),
    L("a1", "Actor Ahn Hyo-seop plays a genius chef. And chef, or cook, in Korean is", "talk", .4), L("a1k", "요리사.", "rice_bowl", ko=True),
    L("a2", "The drama is called Final Table. It's about a cooking competition, and it starts October twenty-fourth.", "excited"),
    L("t0", "And when the food is perfect, you say", "thinking", .45), L("t0k", "맛있다!", "love_heart", ko=True),
    L("t1", "It's delicious!", "party_cake"),
    L("e0", "Will you watch it? Comment below!", "finger_heart", .45)],
  "scenes": [
    {"els": [pic("jinu_red", 420, "h1", w=840, cap="Jinu · KPop Demon Hunters (Netflix)"), pic("ft_teaser1", 960, "h1+2.4", w=840, cap="JTBC 〈파이널 테이블〉 teaser")]},
    {"from": "a1", "els": [pic("ahn_photo", 520, "a1", w=600, crop=(0, 40, 700, 680), cap="안효섭 Ahn Hyo-seop"), word("요리사", "yo-ri-sa", "chef, cook", "y", 1080, "a1k", 140)]},
    {"from": "a2", "els": [pic("art_wt3h", 330, "a2", cap="Wikitree (Korean news) · Sep 2026"), pic("ft_poster", 840, "a2+1.2", w=760), chip("📺 Oct 24 · JTBC", 1190, "a2+3.6", "y")]},
    {"from": "t0", "els": [pic("ft_teaser3", 500, "t0", cap="〈파이널 테이블〉 3rd teaser · JTBC"), word("맛있다!", "ma-sit-da", "it's delicious!", "p", 1040, "t0k", 140, 760)]},
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
