# The ENTIRE Story of The Exorcist: narration voice. Same method as ep08_conjuring/make_voice.py (Adam, eleven_v4,
# /with-timestamps, previous_text / next_text from the neighbouring paragraphs in playback order, one full take per unit,
# no splicing), but the unit is one PARAGRAPH of script_v1.md (hook + 8 chapters, ~60 paragraphs), so a script change
# only re-voices the paragraphs it touches.
# Resume-safe: a paragraph whose voice_orig/<id>.mp3 already exists is skipped unless --force (or --only names it).
# Before any call it checks the ElevenLabs balance and stops if the paragraphs to voice need more than what is left.
# usage: python3 make_voice.py ELEVENLABS_JC_API_KEY [--dry] [--only c1p03,c2p01] [--force]
# Never run with the payg ELEVENLABS_API_KEY without the owner's explicit OK.
import base64, json, os, re, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = 's3TPKV1kjDlVtZbl4Ksh'   # Adam
MODEL = 'eleven_v4'
SCRIPT = os.environ.get('SCRIPT', os.path.join(HERE, 'script_v1.md'))
OUT = os.path.join(HERE, 'voice_orig')


def paragraphs(path=SCRIPT):
    """[{id, chapter, text}] in playback order. id = c<chapter>p<paragraph>, c0 = Hook ... c8 = Outro."""
    s = open(path, encoding='utf-8').read()
    body = '## Hook' + s.split('\n## Hook', 1)[1].split('\n## Fact notes', 1)[0]
    out = []
    for ci, ch in enumerate(re.split(r'(?m)^## ', body)[1:]):
        title, _, text = ch.partition('\n')
        paras = [' '.join(p.split()) for p in re.split(r'\n\s*\n', text) if p.strip()]
        for pi, p in enumerate(paras, 1):
            out.append({'id': f'c{ci}p{pi:02d}', 'chapter': title.strip(), 'text': p})
    return out


def remaining(key):
    r = urllib.request.Request('https://api.elevenlabs.io/v1/user/subscription', headers={'xi-api-key': key})
    d = json.load(urllib.request.urlopen(r, timeout=60))
    return d['character_limit'] - d['character_count'], d.get('next_character_count_reset_unix')


def voice(key, body):
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps',
                               data=json.dumps(body).encode(),
                               headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r, timeout=300))


def main():
    args = sys.argv[1:]
    dry, force = '--dry' in args, '--force' in args
    only = args[args.index('--only') + 1].split(',') if '--only' in args else None
    keyname = args[0] if args and not args[0].startswith('--') else 'ELEVENLABS_JC_API_KEY'
    if keyname == 'ELEVENLABS_API_KEY':
        sys.exit('refusing the payg key: the owner must OK it first')
    P = paragraphs()
    json.dump(P, open(os.path.join(HERE, 'paragraphs.json'), 'w'), ensure_ascii=False, indent=1)
    ids = [p['id'] for p in P]
    if only:
        bad = [i for i in only if i not in ids]
        assert not bad, f'unknown ids {bad}'
    todo = [p for p in P if (p['id'] in only if only else (force or not os.path.exists(os.path.join(OUT, p['id'] + '.mp3'))))]
    need = sum(len(p['text']) for p in todo)
    print(f'paragraphs {len(P)} (to voice {len(todo)}), characters to voice {need}, total {sum(len(p["text"]) for p in P)}')
    longest = max(P, key=lambda p: len(p['text']))
    print('longest paragraph', longest['id'], len(longest['text']), 'chars')
    if dry:
        for p in todo:
            print(p['id'], len(p['text']), p['chapter'][:28], '|', p['text'][:70])
        return
    key = os.environ.get(keyname, '')
    assert key, f'{keyname} is not set'
    left, reset = remaining(key)
    print('balance left', left, 'characters; next reset', reset)
    if left < need + 500:
        sys.exit(f'STOP: need {need} characters but only {left} are left')
    os.makedirs(OUT, exist_ok=True)
    for p in todo:
        i = ids.index(p['id'])
        body = {'text': p['text'], 'model_id': MODEL}
        if i > 0:
            body['previous_text'] = P[i - 1]['text'][-400:]
        if i + 1 < len(P):
            body['next_text'] = P[i + 1]['text'][:300]
        for attempt in range(3):
            try:
                d = voice(key, body)
                break
            except urllib.error.HTTPError as e:
                sys.exit(f'STOP at {p["id"]}: HTTP {e.code} {e.read()[:300]!r}')
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 2:
                    sys.exit(f'STOP at {p["id"]}: network error {e}')
                time.sleep(5 * (attempt + 1))
        open(os.path.join(OUT, p['id'] + '.mp3'), 'wb').write(base64.b64decode(d['audio_base64']))
        json.dump(d['alignment'], open(os.path.join(OUT, p['id'] + '.json'), 'w'))
        print(p['id'], round(d['alignment']['character_end_times_seconds'][-1], 2), 's', flush=True)


if __name__ == '__main__':
    main()
