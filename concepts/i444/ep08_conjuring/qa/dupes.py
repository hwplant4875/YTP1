# EP08 QA: the same moment shown twice. Lists every pair of shots in edl.json whose source spans overlap by more than 0.15 s (same
# clip, or the two clips that hold the same footage, e.g. lr_end t = lr_exorcism t - 330). A shot that build_edl.py resumes after an
# insert continues its own span and is not a repeat. usage: python qa/dupes.py [edl.json]
import json, sys
E = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'edl.json'))
# clip -> [(the clip it repeats, offset, lo, hi)]: for clip times lo..hi, other t = clip t + offset
SAME = {'lr_end': [('lr_exorcism', 330.0, 0, 1e9)],          # lr_end t = lr_exorcism t - 330
        'ach_devil_cz': [('ach_end', -223.5, 223.5, 341.5)],  # ClipZone ach_devil_cz = Movieclips ach_end + 223.5 s (laptop B0)
        'lr_axe': [('lr_family', 48.0, 0, 288)],              # lr_axe t = lr_family t - 48 for lr_axe 0-288 (beats_v1)
        'co_burn_4k': [('n2_burn', 217.0, 70, 166)],
        # v2 (11/18, qa/scene_library_v2.md): re-uploads of the same footage
        'a14_wb_baby': [('a14_cz_haunted', 0.0, 0, 330)], 'a14_basement': [('a14_cz_haunted', 174.0, 0, 150)],
        'a14_baby': [('a14_cz_soul', 170.0, 0, 177)], 'a14_cz_sleeping': [('a14_cz_invasion', 102.0, 0, 402)],
        'a14_s03_rumble': [('a14_cz_attic', 104.0, 0, 137)], 'a14_stairs': [('a14_cz_attic', 241.0, 0, 92)],
        'ach_ferry': [('ach_cz_coineyes', 110.0, 0, 140)], 'ach_hands': [('ach_cz_coineyes', 297.0, 0, 88)],
        'co_doll': [('ach_cz_coineyes', 295.0, 0, 88)], 'ach_wolf': [('ach_cz_stabs', 212.0, 14, 52)],
        'ach_s03_youdid': [('ach_room', 112.0, 0, 136)], 'ach_tv': [('ach_room', 278.0, 0, 88)],
        'ach_wb_basement': [('ach_room', 0.0, 0, 366)], 'ach_wb_tv': [('ach_room', 0.0, 0, 366)],
        'c1_clap': [('c1_best', 0.0, 0, 170)], 'c2_s09_name': [('c2_cz_finale', 173.0, 0, 160)],
        'c2_s10_defiler': [('c2_cz_finale', 354.0, 0, 172)], 'co_valak0': [('n1_cz_possessed', 306.0, 0, 232)],
        'co_neck_b': [('co_neck', -30.0, 30, 210)], 'n2_altar': [('co_neck_b', 484.0, 0, 108)],
        'n2_dr_deliv': [('n2_deliv', 12.0, 0, 127)], 'n2_maurice': [('n2_cz_returns', 25.0, 0, 175)],
        'lr_cz_comp': [('lr_judy', -358.0, 358, 603)], 'cr_stair': [('cr_ar_barn', -1.0, 0, 127)]}          # the same opening scene; ~217 s from the lift (154.3 = 371.3), approximate
spans = []
for S in E['sections']:
    sh = S['shots']
    for k, s in enumerate(sh):
        t, name, tin, sp = s[:4]
        d = (sh[k + 1][0] if k + 1 < len(sh) else S['len']) - t
        a, b = tin, tin + d * (sp or 1.0)
        for other, off, lo, hi in SAME.get(name, []):
            if lo <= a <= hi: name, a, b = other, a + off, b + off; break
        spans.append((name, a, b, S['voice'], round(t, 2), s[1]))
n = 0
for i in range(len(spans)):
    for j in range(i + 1, len(spans)):
        p, q = spans[i], spans[j]
        if p[0] != q[0] or p[0].startswith('still_'): continue   # a still (the poster wall) may come back as a callback
        ov = min(p[2], q[2]) - max(p[1], q[1])
        if ov <= 0.15: continue
        if p[3] == q[3] and abs(p[2] - q[1]) < 0.3: continue   # a running shot resumed after an insert
        print(f'REPEAT {p[0]} {max(p[1], q[1]):.1f}-{min(p[2], q[2]):.1f} ({ov:.1f} s): {p[3]} {p[4]} s ({p[5]}) and {q[3]} {q[4]} s ({q[5]})'); n += 1
print(n, 'repeated spans' if n else 'no repeated spans')
