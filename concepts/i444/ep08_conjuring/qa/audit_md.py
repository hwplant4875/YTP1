# EP08 v6: writes qa/shot_audit_v6.md from edl.json (every shot, its time, the words over it, clip@in, verdict) after the eye audit of
# the contact sheets (qa/audit_sheets.py). WEAK = the verdicts given by eye; every other shot was checked MATCH. usage: python qa/audit_md.py
import json, re, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
E = json.load(open(D + 'edl.json')); W = json.load(open(D + 'voice/words.json'))
cm, cur = {}, None
for l in open(D + 'shots.py', encoding='utf-8').read().split('\n'):
    m = re.search(r"sec\('(s\d\d)'", l)
    if m: cur = m.group(1)
    m = re.search(r"'([a-z0-9_]+)', ([\d.]+), -?[\d.]+.*#\s*(.*)$", l)
    if m and cur: cm[(cur, m.group(1), float(m.group(2)))] = m.group(3).strip()
WEAK = {
 ('s02', 'ach_ferry', 118.0): 'the Ferryman is only a small dark skull face among the coin-eyed souls',
 ('s02', 'ach_ferry', 126.5): 'Mary Ellen in the dark hallway, flashlight flare',
 ('s02', 'ach_cz_stabs', 209.0): 'the Bride face to face with Daniela, dark',
 ('s02', 'ach_devil_cz', 146.0): 'veiled Daniela seen from behind',
 ('s02', 'ach_end', 45.0): 'the case door being forced, hard to read at mid-shot',
 ('s02', 'ach_case', 149.0): 'the doll on the back seat is small',
 ('s03', 'a14_cz_soul', 248.0): '"In this whole movie": the demon taking Leah, unhurt, stands in for its not killing',
 ('s03', 'a14_cz_attic', 306.14): 'the horned demon is on screen only ~0.6 s at the start, then Mia fleeing',
 ('s03', 'a14_cz_invasion', 336.0): 'the cult girl with the doll stands in for "five people die" (no deaths shown on purpose)',
 ('s03', 'a14_wb_baby', 292.0): 'the life-size Annabelle figure at the window',
 ('s04', 'co_mother_c', 288.0): 'Roger and the sheet, generic',
 ('s04', 'c1_exorcism_b', 120.0): 'freed Carolyn with April in the dark crawlspace',
 ('s05', 'c2_cz_voices', 388.5): 'Janet waking on the floor at night, dark close-up',
 ('s05', 'c2_cz_finale', 495.0): 'Lorraine on the wrecked floor, dark',
 ('s05', 'c2_cz_billy', 242.0): "possessed Janet in Bill's chair, quiet moment",
 ('s06', 'lr_s01_baby', 18.3): 'Lorraine\'s evil reflection in the mirror stands in for "the only one"',
 ('s06', 'lr_cz_comp', 92.0): 'the old woman ghost, very dark',
 ('s06', 'lr_exorcism', 4.0): 'Lorraine on the basement floor, very dark',
 ('s06', 'lr_s09_possessed', 40.2): 'possessed Judy crawling stands in for the hanging (rope and attic never shown, by rule)',
 ('s06', 'lr_exorcism', 261.5): 'Ed in silhouette after the attic; the cut-down itself is never shown (rope rule)',
 ('s06', 'lr_priest', 2.0): "Father Gordon's hand, face out of frame",
 ('s07', 'dm_calvary', 64.0): 'Isla and Lorraine face to face in the dark, Lorraine in front',
 ('s07', 'dm_vision', 106.0): 'hands with a rosary (the stabbing is never shown)',
 ('s07', 'dm_cz_herself', 31.0): 'the knife attack in the tunnel, motion blur',
 ('s08', 'cr_well', 96.0): 'the hand pulling Linda at the well, dark',
 ('s08', 'cr_esther_scenes', 60.0): 'Esther before the accident stands in for "the dead daughter"',
 ('s08', 'cr_esther_scenes', 78.0): 'Esther in the dark: her death is voiced only, never shown (gore rule)',
 ('s08', 'cr_trapped', 372.0): 'Sister Charlotte at the closet, dark',
 ('s09', 'co_valak0', 168.35): 'Frenchie (the escape into him is in no clip)',
 ('s09', 'n1_ar_defeats', 134.3): 'Irene takes hold of Valak; the blood in her mouth is not readable at this size',
 ('s10', 'n2_cz_returns', 46.6): "the reliquary's glowing rim in a hand, dark",
 ('s10', 'n2_burn', 376.35): 'Jacques screaming, the burning only as firelight (the burning itself is in s00 and s11)',
 ('s11', 'n2_burn', 373.3): 'Jacques watching, the burning priest above him is off frame',
 ('s11', 'n2_burn', 375.5): 'the priest in the flames, mostly fire by mid-shot',
 ('s11', 'n2_burn', 377.35): 'Jacques screaming up at the burning priest'}
FPS, tg, rows, n, nW = 30, 0.0, [], 0, 0
for S in E['sections']:
    base = round(tg * FPS) / FPS; tg += S['len']; sh = S['shots']
    for k, s in enumerate(sh):
        t1 = sh[k + 1][0] if k + 1 < len(sh) else S['len']; op = s[4] if len(s) > 4 and isinstance(s[4], dict) else {}
        if op.get('ins'):
            x = next((x for x in S['inserts'] if x['s0'] - 0.05 <= s[0] < x['s1']), None); said = '[film] ' + (x['sub'] or x['kind'])
        else:
            out = []
            for ta, tb, s0 in S['pieces']:
                lo, hi = max(s[0], s0), min(t1, s0 + tb - ta)
                if hi > lo: out += [w[2] for w in W[S['voice']] if ta + (lo - s0) - 0.1 <= w[0] < ta + (hi - s0) - 0.1]
            said = ' '.join(out)
        key = (S['voice'], s[1], float(s[2])); v = 'WEAK' if key in WEAK else 'MATCH'; n += 1; nW += v == 'WEAK'
        t = base + s[0]
        rows.append(f"| {S['voice']}#{k:02d} | {int(t // 60)}:{t % 60:05.2f} | {said} | {s[1]}@{s[2]} | {v} | {WEAK.get(key) or cm.get(key, '')} |")
hdr = open(D + 'qa/shot_audit_v6_head.md', encoding='utf-8').read().replace('{N}', str(n)).replace('{MATCH}', str(n - nW)).replace('{WEAK}', str(nW))
open(D + 'qa/shot_audit_v6.md', 'w', encoding='utf-8').write(hdr + '\n'.join(rows) + '\n'); print(n, 'shots,', nW, 'WEAK')
