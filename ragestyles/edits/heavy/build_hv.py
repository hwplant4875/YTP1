"""Heavy test shorts (real record lifts, one event or one athlete per short, original arena / gym voice kept): writes
HV1.json (Raul Flores 511 kg deadlift world record, Giants Live) and HV2.json (Ronnie Coleman heaviest lifts ranked)
next to this file. Story cards at the top, the lift in the middle, slow motion only on the grind, one flash on the
lockout; the owner lays phonk under the finished edit.

    python3 build_hv.py && python3 ../animedit_py.py HV1.json ROOT
"""
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from animedit_ff import FPS, frames_of

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = 'fonts/YouTubeSans-Black.otf'
YEL = '#FFD400'
LIVE = {'warm': 0.0, 'contrast': 1.12, 'sat': 1.08, 'black': 10, 'glow': 0.12, 'sharpen': 0.6, 'grain': 0.01,
        'vignette': 'PI/5'}
BEAT = [{'punch': 0.1}, {'shake': 12}, {'smear': 40}, {'punch': 0.12, 'flash': 'white'}]


def starts_of(shots):
    t, out = 0.0, []
    for s in shots:
        out.append(t)
        t += frames_of(dict(s)) / FPS
    return out, t


def card(text, at, end, y=420, size=112, yellow=(), step=0.0):
    """one caption line; words in `yellow` are drawn yellow; step > 0 reveals word by word"""
    return {'words': [[w, round(at + k * step, 3)] + ([YEL] if w.strip('.,!?') in yellow else [])
                      for k, w in enumerate(text.split())],
            'end': round(end, 3), 'y': y, 'size': size, 'glow': '#000000'}


def said(words, off, end, y, size=100, yellow=()):
    """a voice line word by word from source word times (offset = output at - source in)"""
    return {'words': [[w, round(t + off, 3)] + ([YEL] if w.strip('.,!?') in yellow else []) for w, t in words],
            'end': round(end + off, 3), 'y': y, 'size': size, 'glow': '#000000'}


def beats(shots):
    for k, s in enumerate(shots):
        s.update({'len': 0.5, 'zoom': [s.get('z', 1.0), s.get('z', 1.0) * 1.2], 'ease': 'in', **BEAT[k % 4]})
        s.pop('z', None)
    return shots


def raul():
    OU, GO, WR = 'src/HA/OuagHgC0RYw.mp4', 'src/HA/GoP5D_OHrvc.mp4', 'src/HA/4oHrTDCgVAs.mp4'
    sh = [
        {'src': OU, 'in': 6.0, 'len': 1.4, 'x': 0.5, 'zoom': [1.0, 1.08]},                  # 0 Raul mid-pull (cover)
        {'src': GO, 'in': 6.8, 'len': 2.6, 'x': 0.5, 'zoom': [1.0, 1.06]},                  # 1 Thor 510 lockout
        {'src': GO, 'in': 13.4, 'len': 2.2, 'x': 0.5, 'zoom': [1.0, 1.08]},                 # 2 Thor roars
        {'src': WR, 'in': 133.0, 'len': 1.4, 'x': 0.5, 'zoom': [1.05, 1.15]},               # 3 walk-out
        {'src': WR, 'in': 136.0, 'len': 1.2, 'x': 0.5, 'zoom': [1.05, 1.15]},               # 4 flags
        {'src': WR, 'in': 145.0, 'len': 1.5, 'x': 0.5, 'zoom': [1.3, 1.4]},                 # 5 on stage, name graphic
        {'src': WR, 'in': 159.5, 'len': 1.2, 'x': 0.5, 'zoom': [1.0, 1.06]},                # 6 511 kg on the floor
        {'src': WR, 'in': 165.0, 'len': 1.3, 'x': 0.5, 'zoom': [1.35, 1.45]},               # 7 arms out to the crowd
        {'src': WR, 'in': 174.5, 'len': 1.1, 'x': 0.45, 'zoom': [1.0, 1.06]},               # 8 straps on the bar
        {'src': WR, 'in': 178.0, 'len': 0.8, 'x': 0.6, 'zoom': [1.0, 1.06]},                # 9 his team screams
        {'src': OU, 'in': 3.5, 'out': 9.0, 'speed': [[3.5, 1.0], [5.5, 0.6], [7.5, 1.0]], 'x': 0.5,
         'zoom': [1.0, 1.12]},                                                              # 10 THE PULL, slow on the grind
        {'src': OU, 'in': 9.0, 'len': 1.0, 'x': 0.5, 'zoom': [1.0, 1.06], 'flash': 'white', 'punch': 0.1},  # 11 lockout
    ]
    sh += beats([{'src': WR, 'in': 196.0, 'x': 0.5, 'z': 1.3}, {'src': OU, 'in': 16.0, 'x': 0.5},
                 {'src': WR, 'in': 199.0, 'x': 0.5}, {'src': OU, 'in': 17.0, 'x': 0.5},
                 {'src': WR, 'in': 211.0, 'x': 0.5}, {'src': WR, 'in': 214.5, 'x': 0.5},
                 {'src': WR, 'in': 226.0, 'x': 0.5}, {'src': OU, 'in': 19.0, 'x': 0.5}])
    sh += [{'src': WR, 'in': 211.6, 'len': 3.0, 'x': 0.5, 'zoom': [1.0, 1.08]}]              # end: arms wide
    st, total = starts_of(sh)
    v_thor, v_mtn, v_call, v_wr = st[1] + 0.05, st[1] + 3.85, st[5] + 0.1, st[11] - 0.1   # Thor's call runs 3.7 s
    voice = [{'src': GO, 'in': 3.2, 'out': 6.95, 'at': v_thor},          # "five hundred and ten kilograms"
             {'src': GO, 'in': 29.35, 'out': 31.3, 'at': v_mtn},         # "look upon the mountain"
             {'src': WR, 'in': 155.3, 'out': 161.0, 'at': v_call},       # "Raul Flores! 500 and 11 kilograms"
             {'src': WR, 'in': 194.0, 'out': 198.8, 'at': v_wr},         # "and Flores has a new"
             {'src': WR, 'in': 199.85, 'out': 201.25, 'at': v_wr + 4.9}]  # "world record" (crowd gap cut)
    subs = [card('511 KG.', 0.1, st[1] - 0.05, size=170, yellow={'511'}),
            card('THE WORLD RECORD WAS', st[1] + 0.05, st[2] - 0.05, size=96),
            card('510 KG.', st[1] + 0.6, st[2] - 0.05, y=560, size=150, yellow={'510'}),
            card('HELD BY THE MOUNTAIN.', st[2] + 0.1, st[3] - 0.05, yellow={'MOUNTAIN'}),
            card('THEN A 26-YEAR-OLD', st[3] + 0.1, st[5] - 0.05),
            card('FROM MEXICO', st[4] + 0.05, st[5] - 0.05, y=560, yellow={'MEXICO'}),
            said([('RAUL', 155.38), ('FLORES!', 156.18)], v_call - 155.3, 157.6, y=1240, yellow={'FLORES'}),
            said([('500', 157.8), ('AND', 158.88), ('11', 159.74), ('KILOGRAMS', 160.26)], v_call - 155.3, 161.0,
                 y=1240, yellow={'11'}),
            card('1 KG MORE', st[10] + 0.2, st[11] - 0.05, yellow={'1', 'KG'}),
            card('THAN THE MOUNTAIN.', st[10] + 0.5, st[11] - 0.05, y=560),
            said([('FLORES', 194.7), ('HAS', 196.02), ('A', 196.56), ('NEW', 197.98)], v_wr - 194.0, 198.8, y=1240),
            said([('WORLD', 199.9), ('RECORD!', 200.62)], v_wr + 4.9 - 199.85, 201.25, y=1240, yellow={'RECORD'}),
            card('RECORDS ARE MADE', st[-1] + 0.1, total, size=100),
            card('TO BE BROKEN.', st[-1] + 0.4, total, y=560, size=100, yellow={'BROKEN'}),
            card('NOW GO BREAK YOURS.', v_wr + 6.4, total, y=1240, size=104, yellow={'YOURS'})]
    return {'name': 'HV1_raul_511', 'font': FONT, 'grade': LIVE, 'shots': sh, 'voice': voice, 'subs': subs,
            'fadeout': 0.3}


def ronnie():
    DB, LP, SQ, SQV = ('src/HB/wAsJwWIwlXw.mp4', 'src/HB/9vWgSTdkc2A.mp4', 'src/HB/8rOmcklZCgg.mp4',
                       'src/HB/LVVdlwf1iyM.mp4')
    BOX = {'ratio': '1:1', 'y': 0.5}               # Ronnie's shorts are a 3-panel stack: the middle panel is the shot
    P = {**BOX, 'zoom': [1.08, 1.14]}
    sh = [
        {'src': SQ, 'in': 17.2, 'len': 2.0, **P},                                          # 0 hook: 800 lb squat, bottom
        {'src': DB, 'in': 3.0, 'len': 1.4, **P},                                           # 1 #3 the "200" on the dumbbell
        {'src': DB, 'in': 16.6, 'out': 19.6, **P},                                         # 2 "yeah yeah yeah" (synced)
        {'src': DB, 'in': 24.0, 'len': 2.4, **P},                                          # 3 the press
        {'src': LP, 'in': 33.0, 'len': 1.4, **BOX, 'zoom': [1.0, 1.08]},                   # 4 #2 the plate stack
        {'src': LP, 'in': 57.0, 'out': 58.7, **BOX, 'zoom': [1.0, 1.08]},                  # 5 "time to break the record baby"
        {'src': LP, 'in': 88.0, 'len': 3.0, **BOX, 'zoom': [1.0, 1.1]},                    # 6 reps, "go go go"
        {'src': SQV, 'in': 141.0, 'len': 1.6, **BOX, 'zoom': [1.0, 1.08]},                 # 7 #1 the loaded bar
        {'src': SQ, 'in': 6.6, 'out': 11.0, 'speed': [[6.6, 1.0], [8.4, 0.6], [9.8, 1.0]], **P},   # 8 rep 1, slow at the bottom
        {'src': SQ, 'in': 18.4, 'out': 20.4, **P, 'flash': 'white'},                        # 9 rep 2
    ]
    sh += beats([{'src': SQ, 'in': 11.0, **BOX, 'z': 1.08}, {'src': DB, 'in': 27.0, **BOX, 'z': 1.08},
                 {'src': LP, 'in': 93.0, **BOX}, {'src': SQ, 'in': 19.0, **BOX, 'z': 1.08},
                 {'src': DB, 'in': 31.0, **BOX, 'z': 1.08}, {'src': LP, 'in': 100.0, **BOX},
                 {'src': SQV, 'in': 145.0, **BOX}, {'src': SQ, 'in': 20.0, **BOX, 'z': 1.08}])
    sh += [{'src': SQV, 'in': 97.9, 'out': 101.4, **BOX, 'zoom': [1.0, 1.08]}]            # end: "lightweight baby" (synced)
    st, total = starts_of(sh)
    v_yeah, v_rec, v_go, v_800, v_lw = st[2], st[5], st[6], st[7] + 0.05, st[-1]
    voice = [{'src': DB, 'in': 16.6, 'out': 19.6, 'at': v_yeah},
             {'src': LP, 'in': 57.0, 'out': 58.7, 'at': v_rec},
             {'src': LP, 'in': 88.0, 'out': 91.0, 'at': v_go},
             {'src': SQV, 'in': 10.9, 'out': 15.7, 'at': v_800},       # "this is 800 pounds. 800 solid ass pounds."
             {'src': SQV, 'in': 97.9, 'out': 101.4, 'at': v_lw}]
    TOPA, TOPB, LOW = 250, 400, 1400
    subs = [card('RONNIE COLEMAN', 0.1, st[1] - 0.05, y=TOPA, size=96, yellow={'RONNIE', 'COLEMAN'}),
            card('HEAVIEST LIFTS RANKED', 0.1, st[1] - 0.05, y=TOPB, size=84),
            card('#3', st[1] + 0.05, st[4] - 0.05, y=TOPA, size=150, yellow={'#3'}),
            card('200 LB DUMBBELLS', st[1] + 0.2, st[4] - 0.05, y=TOPB, size=84),
            said([('YEAH!', 17.4), ('YEAH!', 18.08), ('YEAH!', 18.48)], v_yeah - 16.6, 19.6, y=LOW),
            card('#2', st[4] + 0.05, st[7] - 0.05, y=TOPA, size=150, yellow={'#2'}),
            card('2,300 LB LEG PRESS', st[4] + 0.2, st[7] - 0.05, y=TOPB, size=84),
            said([('TIME', 57.26), ('TO', 57.66), ('BREAK', 57.82), ('THE', 57.94), ('RECORD', 58.06), ('BABY!', 58.26)],
                 v_rec - 57.0, 58.7, y=LOW, size=88, yellow={'RECORD'}),
            said([('GO!', 88.16), ('GO!', 89.88)], v_go - 88.0, 91.0, y=LOW, size=110),
            card('#1', st[7] + 0.05, st[10] - 0.05, y=TOPA, size=150, yellow={'#1'}),
            card('800 LB SQUAT. TWICE.', st[7] + 0.2, st[10] - 0.05, y=TOPB, size=84, yellow={'TWICE'}),
            said([('800', 12.02), ('POUNDS.', 12.32), ('800', 13.78), ('SOLID', 14.26), ('POUNDS.', 15.24)],
                 v_800 - 10.9, 15.7, y=LOW, size=88, yellow={'800'}),
            said([("LET'S", 98.02), ('GO,', 98.68)], v_lw - 97.9, 99.9, y=LOW, size=104),
            said([('LIGHTWEIGHT', 99.94), ('BABY!', 100.78)], v_lw - 97.9, 101.4, y=LOW, size=104,
                 yellow={'LIGHTWEIGHT'}),
            card('NOW GO LIFT HEAVY.', st[-1] + 0.5, total, y=TOPA + 60, size=104, yellow={'HEAVY'})]
    return {'name': 'HV2_ronnie_ranked', 'font': FONT, 'grade': LIVE, 'shots': sh, 'voice': voice, 'subs': subs,
            'fadeout': 0.3}


if __name__ == '__main__':
    for code, spec in (('HV1', raul()), ('HV2', ronnie())):
        st, total = starts_of(spec['shots'])
        json.dump(spec, open(os.path.join(HERE, code + '.json'), 'w'), indent=1)
        print(code, spec['name'], f'{total:.2f}s')
