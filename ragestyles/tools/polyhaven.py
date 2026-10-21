"""Download a CC0 Poly Haven asset (gltf model or hdri) into $RS_WORK/3d/<id>/."""
import json, os, sys, urllib.request
OUT = os.path.join(os.environ.get('RS_WORK', '/home/user/rs_work'), '3d')
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'rs-engine/1.0'}), timeout=120).read()
for aid in sys.argv[1:]:
    res = '2k'
    if ':' in aid: aid, res = aid.split(':')
    d = json.loads(get(f'https://api.polyhaven.com/files/{aid}'))
    dst = os.path.join(OUT, aid); os.makedirs(dst, exist_ok=True)
    if 'hdri' in d:
        u = d['hdri'][res]['hdr']['url']; open(f'{dst}/{aid}.hdr', 'wb').write(get(u)); print('hdri', aid); continue
    g = d['gltf'][res]['gltf']
    open(f'{dst}/{aid}.gltf', 'wb').write(get(g['url']))
    for rel, f in g.get('include', {}).items():
        p = os.path.join(dst, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(get(f['url']))
    print('model', aid)
