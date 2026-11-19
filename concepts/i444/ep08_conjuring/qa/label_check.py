# EP08: every shot's top-right film label checked against the film its clip comes from (clip prefix; co_/spooky_nun by the source
# titles in clip_sources_v1.txt; universe by the compilation's time ranges). Also lists film shots with no label. usage: python qa/label_check.py edl.json
import json, sys
E = json.load(open(sys.argv[1], encoding='utf-8'))
FILMS = {'ach': 'Annabelle Comes Home (2019)', 'a14': 'Annabelle (2014)', 'c1': 'The Conjuring (2013)', 'c2': 'The Conjuring 2 (2016)',
         'lr': 'The Conjuring: Last Rites (2025)', 'cr': 'Annabelle: Creation (2017)', 'dm': 'The Conjuring: The Devil Made Me Do It (2021)',
         'n2': 'The Nun II (2023)', 'n1': 'The Nun (2018)'}
# hand lookup from clip_sources_v1.txt (source video titles), independent of build_edl.py's CO map
HAND = {'co_burn': 'n2', 'co_burn_4k': 'n2', 'co_buried': 'n1', 'co_buried_b': 'n1', 'co_neck': 'n2', 'co_stab': 'dm',
        'co_mother': 'c1', 'co_doll': 'ach', 'co_valak0': 'n1', 'spooky_nun': 'n1'}
def truth(name, tin):
    if name == 'universe':   # WB UK compilation: Conjuring 0-936, Conjuring 2 938-1556, DMMDI 1558-1816
        return 'c1' if tin < 937 else 'c2' if tin < 1557 else 'dm' if tin < 1817 else '??'
    if name in HAND: return HAND[name]
    if name.startswith('co_'):
        for k in sorted(HAND, key=len, reverse=True):
            if name.startswith(k): return HAND[k]
        return '??'
    p = name.split('_')[0]
    return p if p in FILMS else None
t0 = 0; n = 0; bad = []; nolab = []
for S in E['sections']:
    films = [o for o in S['overlays'] if o[0] == 'film']
    for k, (t, name, tin, sp, *r) in enumerate(S['shots']):
        n += 1; want = truth(name, tin); op = r[0] if r else {}
        lab = [o[1] for o in films if o[2] <= t + 1e-6 < o[3]]
        tag = f"{S['voice']}#{k:02d} {(t0+t)//60:.0f}:{(t0+t)%60:05.2f} {name}@{tin}"
        if name == 'universe' and op.get('f') != want: bad.append(f"{tag}: f={op.get('f')} but footage time says {want}")
        if lab:
            if want is None or lab[0] != FILMS.get(want): bad.append(f"{tag}: label '{lab[0]}' but clip is {FILMS.get(want, want)}")
        elif want: nolab.append(f"{tag} ({want})")
    t0 += S['len']
print('shots', n); print('MISMATCH', len(bad)); print(*bad, sep='\n')
print('unlabelled film shots (card / cold-open / rules regions)', len(nolab)); print(*nolab, sep='\n')
