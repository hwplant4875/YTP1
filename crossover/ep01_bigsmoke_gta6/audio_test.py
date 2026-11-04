# audio events anchored to actual (frame-rounded) shot starts from the EDL
import importlib.util, os
_spec=importlib.util.spec_from_file_location('edl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'edl_test.py'))
_e=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_e)
ST={}; _n=0
for _s in _e.SHOTS: ST[_s['id']]=_n/30; _n+=round(_s['dur']*30)
TOTAL=_n/30
BGM=os.environ.get('BGM','sfx/bgm_keep_it_coming.wav')
O=375.652  # BG_b offset (BGb stems are HD-file time)
EA=248.427
D='aud/sephd/htdemucs/'
# (name, file, src_start, src_end, t_place, target_lufs, fade_in, fade_out, filter)
EVENTS=[
 ('amb',  D+'Ea/no_vocals.wav', 272.05-EA, 272.05-EA+ST['S1']+0.10, 0.00, -34, 0.25, 0.35, 'lowpass=f=6000'),
 ('door', 'sfx/door_wood.wav',  0.00, 1.40, ST['C1']+0.50, -24, 0.0, 0.3, None),
 ('yell', D+'BGb/vocals.wav',   386.60-O, 388.85-O, ST['C2']-0.10, -15, 0.02, 0.08, None),
 ('whsh', 'sfx/bat_whoosh.wav', 0.00, 1.20, ST['C2'], -25, 0.0, 0.3, None),
 ('ohdog',D+'BGb/vocals.wav',   396.15-O, 399.52-O, ST['C5']-0.25-(397.14-396.15), -16, 0.04, 0.10, None),
 ('hands',D+'T2/vocals.wav',    74.38, 76.48, ST['S1'], -15, 0.02, 0.06, None),
 ('stay', D+'T2/vocals.wav',    76.58, 77.58, ST['S2']+0.02, -15, 0.02, 0.08, None),
 ('order',D+'DT/vocals.wav',    82.38, 96.98, ST['S4']-0.02, -16, 0.02, 0.10, None),
 ('bgm',  BGM, 0.00, ST['S18']-ST['S1'], ST['S1'], -29.5, 0.01, 0.04, 'highshelf=f=3000:g=-4'),
 ('cock', 'sfx/gun_cock.wav',   0.00, 0.99, ST['S18']+0.06, -16, 0.0, 0.05, None),
]
