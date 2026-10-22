# Download candidate photos from Wikimedia Commons for the catacombs video (run on the laptop; the server gets 429).
# usage: python get_photos.py OUT_DIR
# For each slot it searches Commons (File namespace), keeps freely licensed results (CC0 / PD / CC BY / CC BY-SA),
# downloads up to 6 candidates at 1920 px, writes credits.json and a contact sheet per slot (needs Pillow).
import json, os, sys, time, urllib.parse, urllib.request

UA = 'PEEKdocs/1.0 (https://www.youtube.com/@the_peek_inside) python-urllib'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'photos'
SLOTS = {
    'b12_notre_dame': 'Notre-Dame de Paris facade',
    'b12_louvre': 'Louvre Cour Carree facade',
    'b19_innocents': 'Cimetiere des Innocents gravure',
    'b20_charnier': 'charniers des Innocents',
    'b21_innocents_1780': 'Fontaine des Innocents cimetiere 1780',
    'b23_transfer': 'translation ossements catacombes nuit',
    'b24_ossuary_wide': 'Catacombes de Paris ossuaire',
    'b25_bones_pile': 'Catacombs of Paris bones',
    'b26_bone_wall_heart': 'Catacombes de Paris coeur ossements',
    'b26_bone_barrel': 'Catacombes de Paris tonneau ossements',
    'b27_empire_sign': 'Arrete c\'est ici l\'empire de la mort',
    'b28_stairs': 'Catacombes de Paris escalier',
    'b28_tunnel': 'Catacombes de Paris galerie',
}
OK = ('cc0', 'public domain', 'pd', 'cc by', 'cc-by', 'cc by-sa', 'cc-by-sa')


def get(url):
    for i in range(5):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60).read()
        except Exception as e:
            time.sleep(3 * (i + 1))
    raise RuntimeError(url)


def api(params):
    params.update(format='json')
    return json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)))


def main():
    os.makedirs(OUT, exist_ok=True)
    credits = {}
    for slot, q in SLOTS.items():
        d = os.path.join(OUT, slot); os.makedirs(d, exist_ok=True)
        r = api({'action': 'query', 'generator': 'search', 'gsrsearch': q + ' filetype:bitmap', 'gsrnamespace': 6,
                 'gsrlimit': 20, 'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size', 'iiurlwidth': 1920})
        pages = sorted((r.get('query') or {}).get('pages', {}).values(), key=lambda p: p.get('index', 99))
        n = 0
        for p in pages:
            ii = (p.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata', {})
            lic = md.get('LicenseShortName', {}).get('value', '')
            if not any(k in lic.lower() for k in OK) or ii.get('width', 0) < 1200:
                continue
            fn = f'{n + 1}.jpg'
            open(os.path.join(d, fn), 'wb').write(get(ii.get('thumburl') or ii['url']))
            artist = md.get('Artist', {}).get('value', '')
            import re
            artist = re.sub('<[^>]+>', '', artist).strip()
            credits[f'{slot}/{fn}'] = {'title': p['title'], 'license': lic, 'artist': artist,
                                       'page': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(p['title'].replace(' ', '_'))}
            n += 1; time.sleep(1.0)
            if n >= 6: break
        print(slot, n, flush=True)
        try:
            from PIL import Image, ImageDraw
            ims = [Image.open(os.path.join(d, f'{i + 1}.jpg')).convert('RGB') for i in range(n)]
            if ims:
                sheet = Image.new('RGB', (3 * 480, ((n + 2) // 3) * 290), (20, 20, 20))
                for i, im in enumerate(ims):
                    im.thumbnail((470, 270)); sheet.paste(im, ((i % 3) * 480 + 5, (i // 3) * 290 + 5))
                    ImageDraw.Draw(sheet).text(((i % 3) * 480 + 10, (i // 3) * 290 + 8), str(i + 1), fill=(255, 255, 0))
                sheet.save(os.path.join(d, 'sheet.jpg'))
        except Exception as e:
            print('sheet failed', e)
    json.dump(credits, open(os.path.join(OUT, 'credits.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
