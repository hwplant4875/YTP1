"""Download CC0 Poly Haven assets for the Riddle House room (no login needed)."""
import json, os, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
API = "https://api.polyhaven.com/files/"
UA = {"User-Agent": "YouElsewhere-room-builder/1.0"}

MODELS = ["GreenChair_01", "round_wooden_table_01", "book_encyclopedia_set_01",
          "mantel_clock_01", "brass_candleholders", "ornate_mirror_01",
          "fancy_picture_frame_01", "GothicCommode_01"]
TEXTURES = {"decrepit_wallpaper": "2k", "old_wooden_floor_02": "2k", "dirty_carpet": "2k",
            "medieval_red_brick": "2k", "weathered_planks": "2k", "dark_wood": "2k",
            "bark_brown_01": "1k", "wood_cabinet_worn_long": "2k", "worn_plaster_wall": "2k",
            "forest_floor": "1k"}
HDRI = ("moonlit_golf", "2k")


def get(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r, open(dest, "wb") as f:
        f.write(r.read())
    print("  got", os.path.relpath(dest, ROOT))


def files(asset):
    with urllib.request.urlopen(urllib.request.Request(API + asset, headers=UA)) as r:
        return json.load(r)


for m in MODELS:
    print(m)
    g = files(m)["gltf"]["2k"]["gltf"]
    d = os.path.join(ROOT, "models", m)
    get(g["url"], os.path.join(d, os.path.basename(g["url"])))
    for rel, inc in g["include"].items():
        get(inc["url"], os.path.join(d, rel))

for t, res in TEXTURES.items():
    print(t)
    f = files(t)
    for key in ("Diffuse", "nor_gl", "Rough", "Displacement", "AO"):
        if key in f:
            u = f[key][res]["jpg"]["url"]
            get(u, os.path.join(ROOT, "textures", t, os.path.basename(u)))

print(HDRI[0])
u = files(HDRI[0])["hdri"][HDRI[1]]["hdr"]["url"]
get(u, os.path.join(ROOT, "hdri", os.path.basename(u)))
print("done")
