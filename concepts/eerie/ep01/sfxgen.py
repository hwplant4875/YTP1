import json, os, sys, urllib.request
out = sys.argv[1]; key = os.environ['ELEVENLABS_JC_API_KEY']
REQ = {
 'gsoft1': ('very soft short muffled VHS tape flicker, gentle low analog static blip, warm, quiet, no harsh high frequencies', 0.6),
 'gsoft2': ('gentle soft tape warble glitch, muffled, short, warm and quiet, no hiss, no beep', 0.6),
 'gsoft3': ('soft brief low analog interference crackle, muffled, gentle, quiet', 0.7),
 'thud': ('single soft deep warm cinematic low thud, muffled, gentle impact, no distortion, no ring', 2.0),
 'meow_raw': ('a single long slow realistic house cat meow, close microphone, dry, no background', 2.0),
 'growl': ('a low deep menacing cat growl, close, slow, dark, realistic', 2.5),
 'scream': ('a short muffled human scream of terror heard from inside a bedroom, cut off abruptly', 1.6),
 'dooropen': ('a wooden bedroom door handle pressed down and the door creaking open slowly, close', 2.0),
 'swipe': ('a single extremely fast sharp swipe whoosh, like claws slicing air, very short', 0.5),
}
for k, (p, d) in REQ.items():
    f = os.path.join(out, k + '.mp3')
    if os.path.exists(f): continue
    body = {'text': p, 'duration_seconds': d, 'prompt_influence': 0.6}
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    open(f, 'wb').write(urllib.request.urlopen(req).read()); print(k, 'ok')
