"""Training-motivation test shorts (real reps from films/documentaries, one work per short): writes TR1.json (Rocky IV
montage) and TR2.json (Pumping Iron) next to this file. Captions are plain story cards (white, black shadow, one yellow
keyword), slow motion only on the grind, one flash on the payoff; the owner lays phonk under the finished edit.

    python3 build_tr.py && python3 ../animedit_py.py TR1.json ROOT
"""
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from animedit_ff import FPS, frames_of

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = 'fonts/YouTubeSans-Black.otf'
YEL = '#FFD400'
FILM = {'warm': 0.0, 'contrast': 1.12, 'sat': 1.05, 'black': 10, 'glow': 0.15, 'sharpen': 0.6, 'grain': 0.012,
        'vignette': 'PI/5'}
DROP = [{'punch': 0.1}, {'shake': 12}, {'smear': 50}, {'punch': 0.12, 'flash': 'white'}]   # every 4th beat hits harder


def starts_of(shots):
    t, out = 0.0, []
    for s in shots:
        out.append(t)
        t += frames_of(dict(s)) / FPS
    return out, t


def card(text, at, end, y=1240, size=108, yellow=(), step=0.0):
    """one caption line; words in `yellow` are drawn yellow; step > 0 reveals word by word"""
    return {'words': [[w, round(at + k * step, 3)] + ([YEL] if w.strip('.,!?') in yellow else [])
                      for k, w in enumerate(text.split())],
            'end': round(end, 3), 'y': y, 'size': size, 'glow': '#000000'}


def drop(shots):
    for k, s in enumerate(shots):
        s.update({'len': 0.5, 'zoom': [1.0, 1.22], 'ease': 'in', **DROP[k % 4]})
    return shots


def rocky():
    R = 'src/MR/A_hLdPRsssE.mp4'
    sh = [
        {'src': R, 'in': 423.4, 'len': 1.4, 'x': 0.35, 'zoom': [1.0, 1.1]},                       # 0 Drago, gritted
        {'src': R, 'in': 381.6, 'len': 0.5, 'ratio': '16:9', 'zoom': [1.1, 1.14]},                 # 1 1850 (zoom keeps the corner tag out)
        {'src': R, 'in': 382.95, 'len': 0.5, 'ratio': '16:9', 'zoom': [1.1, 1.14]},                # 2 1990
        {'src': R, 'in': 384.75, 'len': 0.6, 'ratio': '16:9', 'zoom': [1.1, 1.18], 'punch': 0.1, 'shake': 10},  # 3 2045
        {'src': R, 'in': 405.0, 'len': 0.5, 'x': 0.55, 'zoom': [1.0, 1.08]},                      # 4 syringe
        {'src': R, 'in': 406.95, 'len': 1.0, 'x': 0.5, 'zoom': [1.0, 1.15]},                      # 5 needle
        {'src': R, 'in': 50.7, 'len': 1.7, 'x': 0.55, 'zoom': [1.0, 1.1]},                        # 6 Rocky in the snow
        {'src': R, 'in': 128.3, 'len': 1.8, 'speed': 0.8, 'x': 0.65, 'zoom': [1.0, 1.06]},        # 7 sled crawl
        {'src': R, 'in': 139.9, 'len': 1.2, 'x': 0.7, 'zoom': [1.0, 1.06]},                       # 8 sled crawl
        {'src': R, 'in': 153.3, 'len': 1.4, 'x': 0.4, 'zoom': [1.0, 1.06]},                       # 9 log carry
        {'src': R, 'in': 159.3, 'len': 1.6, 'x': 0.5, 'zoom': [1.0, 1.06]},                       # 10 log carry
        {'src': R, 'in': 323.3, 'len': 0.5, 'x': 0.55, 'punch': 0.06},                            # 11 axe up
        {'src': R, 'in': 328.0, 'len': 0.8, 'x': 0.45, 'punch': 0.06},                            # 12 chop
        {'src': R, 'in': 332.6, 'len': 0.5, 'x': 0.78, 'punch': 0.06},                            # 13 chop wide
        {'src': R, 'in': 425.3, 'len': 1.6, 'x': 0.5, 'zoom': [1.0, 1.08]},                       # 14 pull, barn
        {'src': R, 'in': 434.8, 'len': 1.2, 'x': 0.45, 'zoom': [1.0, 1.08]},                      # 15 pull, face
        {'src': R, 'in': 455.55, 'len': 0.5, 'x': 0.5, 'strobe': [0.0, 0.5]},                     # 16 pre-drop
    ]
    sh += drop([{'src': R, 'in': t, 'x': x} for t, x in [
        (456.0, 0.55), (463.2, 0.7), (484.6, 0.32), (485.8, 0.32), (486.7, 0.55), (493.2, 0.5),
        (496.8, 0.4), (505.9, 0.5), (513.6, 0.5), (520.2, 0.5), (524.0, 0.5), (486.0, 0.32)]])
    sh += [{'src': R, 'in': 527.0, 'len': 1.3, 'x': 0.65, 'zoom': [1.0, 1.06]},
           {'src': R, 'in': 528.3, 'len': 2.4, 'speed': 0.6, 'x': 0.6, 'zoom': [1.0, 1.08], 'flash': 'white'}]
    st, total = starts_of(sh)
    subs = [card('HE HAD MACHINES.', 0.15, st[4] - 0.05, yellow={'MACHINES'}),
            card('HE HAD STEROIDS.', st[4] + 0.1, st[6] - 0.05, yellow={'STEROIDS'}),
            card('ROCKY HAD NOTHING.', st[6] + 0.15, st[7] - 0.05, yellow={'NOTHING'}),
            card('NO GYM.', st[7] + 0.2, st[9] - 0.05, size=124, yellow={'GYM'}),
            card('NO MACHINES.', st[9] + 0.1, st[11] - 0.05, size=124, yellow={'MACHINES'}),
            card('NO EXCUSES.', st[11] + 0.05, st[14] - 0.05, size=124, yellow={'EXCUSES'}),
            card('JUST WORK.', st[14] + 0.1, st[16], size=124, yellow={'WORK'}),
            card("WHAT'S YOUR EXCUSE?", st[-1] + 0.35, total, size=112, yellow={'EXCUSE'})]
    return {'name': 'TR1_rocky_no_excuses', 'font': FONT, 'grade': {**FILM, 'warm': -0.02}, 'shots': sh, 'voice': [],
            'subs': subs, 'fadeout': 0.3}


def arnold():
    A, P = 'src/MA/my6IroYcyEI.mp4', 'src/MA/p4KQbnpyLrY.mp4'
    sh = [
        {'src': A, 'in': 265.0, 'len': 1.8, 'x': 0.5, 'zoom': [1.0, 1.1]},       # 0 gritted face (cover)
        {'src': A, 'in': 53.3, 'len': 1.0, 'x': 0.35, 'zoom': [1.0, 1.06]},      # 1 side chest
        {'src': A, 'in': 46.0, 'len': 1.2, 'x': 0.45, 'zoom': [1.0, 1.06]},      # 2 pose
        {'src': A, 'in': 56.4, 'len': 1.3, 'x': 0.45, 'zoom': [1.0, 1.06]},      # 3 legs, 1975 Olympia
        {'src': A, 'in': 30.0, 'len': 2.1, 'x': 0.6, 'zoom': [1.0, 1.06]},       # 4 posing to the press
        {'src': A, 'in': 64.0, 'len': 1.0, 'x': 0.5, 'zoom': [1.0, 1.06]},       # 5 front pose
        {'src': A, 'in': 52.6, 'len': 0.6, 'x': 0.45},                           # 6 under the bar
        {'src': A, 'in': 118.0, 'len': 1.2, 'x': 0.55, 'zoom': [1.0, 1.06]},     # 7 loading plates
        {'src': A, 'in': 125.0, 'len': 1.3, 'x': 0.5, 'zoom': [1.0, 1.06]},      # 8 grabbing the bar
        {'src': A, 'in': 155.0, 'len': 2.0, 'speed': 0.8, 'x': 0.4, 'zoom': [1.0, 1.08]},   # 9 squat grind
        {'src': A, 'in': 183.0, 'len': 1.8, 'x': 0.5, 'zoom': [1.0, 1.08]},      # 10 bench, face
        {'src': A, 'in': 189.5, 'len': 1.0, 'x': 0.45, 'zoom': [1.0, 1.08]},     # 11 bench grind
        {'src': A, 'in': 61.0, 'len': 0.9, 'x': 0.5},                            # 12 row scream
        {'src': A, 'in': 100.0, 'len': 1.0, 'x': 0.45},                          # 13 row
        {'src': A, 'in': 252.0, 'len': 0.8, 'x': 0.5},                           # 14 row
        {'src': A, 'in': 270.0, 'len': 0.5, 'x': 0.5, 'strobe': [0.0, 0.5]},     # 15 pre-drop
    ]
    sh += drop([{'src': A, 'in': t, 'x': x} for t, x in [
        (265.5, 0.5), (155.6, 0.4), (98.5, 0.45), (40.0, 0.5), (183.8, 0.5), (46.6, 0.45),
        (270.6, 0.5), (130.0, 0.4), (280.0, 0.5), (54.0, 0.4), (61.5, 0.5), (275.0, 0.5)]])
    sh += [{'src': A, 'in': 283.0, 'len': 1.5, 'x': 0.5, 'zoom': [1.0, 1.06]},
           {'src': A, 'in': 286.4, 'len': 2.2, 'speed': 0.7, 'x': 0.5, 'zoom': [1.0, 1.08], 'flash': 'white'}]
    st, total = starts_of(sh)
    # narrator lines (Pumping Iron); source word times from faster-whisper, placed with offset at - in
    v1, v2, v3, v4 = 0.3, max(st[4] + 0.05, 5.85), st[6] + 0.05, st[10] + 0.1
    voice = [{'src': P, 'in': 151.7, 'out': 157.1, 'at': v1}, {'src': P, 'in': 157.95, 'out': 160.05, 'at': v2},
             {'src': P, 'in': 160.5, 'out': 163.5, 'at': v3}, {'src': P, 'in': 105.45, 'out': 108.45, 'at': v4}]

    def line(words, off, end, yellow=()):
        return {'words': [[w, round(t + off, 3)] + ([YEL] if w.strip('.,!?') in yellow else []) for w, t in words],
                'end': round(end + off, 3), 'y': 1240, 'size': 112, 'glow': '#000000'}
    o1, o2, o3, o4 = v1 - 151.7, v2 - 157.95, v3 - 160.5, v4 - 105.45
    subs = [dict(line([('ARNOLD', 151.78)], o1, 153.35), y=1105),
            line([('SCHWARZENEGGER', 152.38)], o1, 153.35, {'SCHWARZENEGGER'}),
            line([('28', 153.40), ('YEARS', 153.80), ('OLD.', 154.06)], o1, 154.72, {'28'}),
            line([('6', 154.78), ('FOOT', 155.02), ('2.', 155.24)], o1, 155.9),
            line([('240', 155.96), ('POUNDS.', 156.54)], o1, 157.0, {'240'}),
            line([('MR.', 158.0), ('OLYMPIA', 158.46)], o2, 158.76, {'OLYMPIA'}),
            line([('FOR', 158.78), ('THE', 158.92), ('PAST', 159.02), ('FIVE', 159.32), ('YEARS.', 159.6)], o2, 160.05,
                 {'FIVE'}),
            line([('HE', 160.58), ('IS', 160.7), ('PREPARING', 160.78)], o3, 161.12),
            line([('TO', 161.16), ('DEFEND', 161.32), ('HIS', 161.58), ('TITLE', 161.78)], o3, 162.0, {'TITLE'}),
            line([('THIS', 162.02), ('YEAR', 162.26)], o3, 162.48),
            line([('FOR', 162.5), ('THE', 162.7), ('LAST', 162.8), ('TIME.', 163.06)], o3, 163.6, {'LAST', 'TIME'}),
            line([('COME', 105.6), ('ON,', 105.84), ('COME', 107.56), ('ON!', 108.14)], o4, 108.45, {'ON'}),
            card('HE WON. AGAIN.', st[-2] + 0.2, st[-1] - 0.05, yellow={'AGAIN'}),
            card('NOW GO TRAIN.', st[-1] + 0.35, total, size=124, yellow={'TRAIN'})]
    return {'name': 'TR2_arnold_last_time', 'font': FONT, 'grade': FILM, 'shots': sh, 'voice': voice, 'subs': subs,
            'fadeout': 0.3}


if __name__ == '__main__':
    for code, spec in (('TR1', rocky()), ('TR2', arnold())):
        st, total = starts_of(spec['shots'])
        json.dump(spec, open(os.path.join(HERE, code + '.json'), 'w'), indent=1)
        print(code, spec['name'], f'{total:.2f}s', 'drop at', f"{st[[i for i, s in enumerate(spec['shots']) if s.get('ease') == 'in'][0]]:.2f}s")
