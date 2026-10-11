import json, subprocess
gap = {"h1": .25, "h2": .08, "g_n": .45, "g_s": .65, "c0": .55, "g_c1": .35, "g_c3": .3, "g_c5": .45, "g_a0": .6, "g_a2": .45, "r0": .75, "r1": .4, "e0": .5}
def dur(g): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"vo/{g}.wav"]))
t = 0; T = {}; G = {}
for g, spans in json.load(open("groups.json")):
    t += gap[g]; G[g] = round(t, 3)
    for k, a, b in spans: T[k] = [round(t + a, 3), round(t + b, 3)]
    t += dur(g)
T["END"] = round(t + 1.6, 3)
json.dump(T, open("timeline.json", "w"), indent=1); json.dump(G, open("group_starts.json", "w"), indent=1); print(T["END"])
