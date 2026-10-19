import json,sys,urllib.request,os
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})))
def dl(u,p):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    if not os.path.exists(p): os.system(f"curl -sL -A Mozilla -o \"{p}\" \"{u}\"")
A='/tmp/claude-0/vz/assets'
for a in sys.argv[1:]:
    kind,id_,res=a.split(':')
    f=get(f'https://api.polyhaven.com/files/{id_}')
    if kind=='hdri':
        dl(f['hdri'][res]['hdr']['url'],f'{A}/{id_}.hdr')
    elif kind=='tex':
        b=f['Diffuse'] if 'Diffuse' in f else f['diff_png'] if 'diff_png' in f else None
        for m in ['Diffuse','nor_gl','Rough','AO']:
            if m in f: dl(f[m][res]['jpg']['url'],f'{A}/{id_}/{m}.jpg')
    else:
        g=f['gltf'][res]['gltf']
        dl(g['url'],f'{A}/{id_}/{id_}.gltf')
        for rel,v in g['include'].items(): dl(v['url'],f'{A}/{id_}/{rel}')
    print('ok',id_)
