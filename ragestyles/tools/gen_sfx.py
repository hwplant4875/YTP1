"""Generate the RageStyles SFX pack with ElevenLabs sound generation (cached by name)."""
import json, os, sys, urllib.request
OUT = os.environ.get('RS_SFX', '/home/user/rs_work/sfx')
PACK = {
  'whoosh_fast': ('fast clean air whoosh swoosh transition, short, punchy, no music', 0.8),
  'whoosh_deep': ('deep heavy cinematic whoosh pass-by, low end, transition', 1.2),
  'sub_hit': ('808 sub bass hit boom, deep punchy low frequency impact, clean, edit sound effect', 1.5),
  'braam': ('massive cinematic braam impact hit, dark trailer style, deep brass and sub', 2.5),
  'impact_metal': ('heavy metal weight plates slam on the floor, gym, loud clang impact', 1.2),
  'riser': ('short tension riser building up, rising white noise swell ending abruptly', 2.0),
  'flash': ('camera flash pop with bright shimmer, photo shutter click', 0.7),
  'glitch': ('digital glitch stutter, short data corruption burst', 0.6),
  'tick': ('single crisp UI tick click, short', 0.5),
  'ding': ('bright satisfying notification ding, achievement unlocked', 0.9),
  'heartbeat': ('two deep heartbeat thumps, cinematic, low', 1.2),
  'crowd_ooh': ('small crowd of people reacting oooh amazed gasp', 1.6),
  'thud_heavy': ('very heavy object dropped onto metal bar, deep thud with metallic ring', 1.0),
  'car_land': ('car dropped from height lands heavily, suspension crunch, metal thump', 1.4),
  'tape_stop': ('tape stop slowdown sound effect', 0.8),
  'pop': ('soft quick pop for text appearing, bubbly, short', 0.5),
  'swipe': ('quick paper-like swipe swish for UI card sliding in', 0.5),
  'bass_drop': ('deep sub bass drop dropping in pitch, cinematic, 808', 2.0),
  'chain_rattle': ('heavy chain rattle and clank, gym barbell plates shaking', 1.0),
  'rumble': ('low earthquake rumble building, deep', 2.0),
  'snap_zoom': ('fast zoom in swoosh with a click at the end, camera snap', 0.5),
  'grunt_crowd': ('gym crowd cheering and yelling in excitement, short burst', 2.0),
}
key = os.environ['ELEVENLABS_API_KEY']
os.makedirs(OUT, exist_ok=True)
for name, (text, dur) in PACK.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]: continue
    p = f'{OUT}/{name}.mp3'
    if os.path.exists(p): continue
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', method='POST',
        data=json.dumps({'text': text, 'duration_seconds': dur, 'prompt_influence': 0.6}).encode(),
        headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r: open(p, 'wb').write(r.read())
        print('ok', name)
    except Exception as e: print('fail', name, e, getattr(e, 'read', lambda: b'')()[:200])
