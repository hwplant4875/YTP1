"""Build simplified occupation-zone and Berlin-sector polygons (lon/lat) for graphics2d.py.
Sources: isellsoap/deutschlandGeoJSON (states), Berlin LOR Ortsteile (Geoportal Berlin / TSB open data)."""
import json, sys
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union

states = json.load(open(sys.argv[1]))["features"]
orts = json.load(open(sys.argv[2]))["features"]
st = {f["properties"]["name"]: shape(f["geometry"]).buffer(0) for f in states}
ZONE = {"soviet": ["Mecklenburg-Vorpommern", "Brandenburg", "Sachsen-Anhalt", "Sachsen", "Thüringen", "Berlin"],
        "british": ["Schleswig-Holstein", "Hamburg", "Niedersachsen", "Nordrhein-Westfalen"],
        "american": ["Bayern", "Hessen", "Bremen"],
        "french": ["Rheinland-Pfalz", "Saarland"]}
zones = {z: unary_union([st[n] for n in ns]) for z, ns in ZONE.items()}
bw = st["Baden-Württemberg"]
north = box(7, 48.72, 11, 50)   # US got Nordwürttemberg/Nordbaden (roughly north of the Karlsruhe-Ulm motorway)
zones["american"] = unary_union([zones["american"], bw.intersection(north)])
zones["french"] = unary_union([zones["french"], bw.difference(north)])
germany = unary_union(list(st.values()))
SECT = {"soviet": ["Mitte", "Friedrichshain-Kreuzberg:Friedrichshain", "Pankow", "Treptow-Köpenick", "Lichtenberg", "Marzahn-Hellersdorf"],
        "american": ["Steglitz-Zehlendorf", "Tempelhof-Schöneberg", "Neukölln", "Friedrichshain-Kreuzberg:Kreuzberg"],
        "british": ["Charlottenburg-Wilmersdorf", "Spandau", "Mitte:Moabit", "Mitte:Hansaviertel", "Mitte:Tiergarten"],
        "french": ["Reinickendorf", "Mitte:Wedding", "Mitte:Gesundbrunnen"]}
def sector(o):
    b, n = o["BEZIRK"], o["OTEIL"]
    for s, keys in SECT.items():
        if f"{b}:{n}" in keys:
            return s
    if b == "Mitte" and n == "Mitte":
        return "soviet"
    for s, keys in SECT.items():
        if b in keys:
            return s
    raise SystemExit(f"no sector for {b}/{n}")
parts = {}
for f in orts:
    parts.setdefault(sector(f["properties"]), []).append(shape(f["geometry"]).buffer(0))
sectors = {s: unary_union(p).buffer(0.0004).buffer(-0.0004) for s, p in parts.items()}
west = unary_union([sectors[s] for s in ("american", "british", "french")])
wall_inner = sectors["soviet"].buffer(0.0005).intersection(west.boundary)   # the East/West sector line inside the city
out = {"germany": mapping(germany.simplify(0.01)),
       "zones": {z: mapping(g.simplify(0.01)) for z, g in zones.items()},
       "berlin": {s: mapping(g.simplify(0.0006)) for s, g in sectors.items()},
       "berlin_outline": mapping(unary_union(list(sectors.values())).simplify(0.0006)),
       "wall_inner": mapping(wall_inner.simplify(0.0004))}
json.dump(out, open("geo_zones.json", "w"))
print({k: len(json.dumps(v)) for k, v in out.items()})
