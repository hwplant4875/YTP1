# You, Elsewhere EP4 (Christmas Eve 2009): ~30 min public-domain carol suite, jazz piano trio, EP3 library sound.
# Brief: you_elsewhere/ep04_christmas2009/MUSIC_BRIEF.md. First chorus of every carol = melody exactly as written
# (straight, one register); chords keep the melody note (clashing comp notes dropped by EP3's clear_of_melody);
# variations/solos only after the first chorus. Celesta doubles some first choruses, soft sleigh bells on two
# up-tempo carols. No ride; soft brushes; bass always present. 4 s crossfades, -17 LUFS.
# Melodies are typed from published scores and parsed from ABC so the notes can be checked line by line:
#   Wikipedia LilyPond scores: Silent Night (contemporary), O Tannenbaum, Away in a Manger (Kirkpatrick),
#   Hark! (Mendelssohn, IMSLP full score), Angels We Have Heard (Barnes arr.), God Rest Ye.
#   P. G. Hardy Christmas tunebook (ABC): First Noel, Deck the Halls, Jingle Bells (Pierpont 1857),
#   We Wish You, Good King Wenceslas (Piae Cantiones), O Holy Night (Adam 1847), O Tannenbaum, Silent Night.
#   Jolly Old Saint Nicholas: Stephen Merrony ABC. Carol of the Bells: Leontovych's Shchedryk ostinato (1916).
# usage: python compose_christmas_suite.py [track ids...]   (no args = all tracks + join)
import os, re, sys, json, subprocess, importlib.util

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

HERE = os.path.dirname(os.path.abspath(__file__))
ep3 = load('ep3', os.path.join(HERE, '..', '..', 'ep03_malfoid_library', 'music', 'compose_library_suite.py'))
cs = ep3.cs

OUT = r'C:\Users\hw549\Downloads\YTP1\YouElsewhere\ep04_christmas2009\music'
WORK = r'E:\YTP2\YouElsewhere\ep04_christmas2009\suite_tracks'      # stems on E: (C: is nearly full)
MISC = r'C:\Users\hw549\Downloads\YTP1\_samples\VSCO-2-CE-master\Miscellania Raw\Misc 2'
TARGET = 122        # seconds per track before crossfades (15 tracks -> ~30:00)

# ------------------------------------------------------------------ ABC -> (midi, beats)
KEYS = {'C': {}, 'G': {'F': 1}, 'D': {'F': 1, 'C': 1}, 'F': {'B': -1}, 'Bb': {'B': -1, 'E': -1}, 'Gm': {'B': -1, 'E': -1}}
TOK = re.compile(r"(\^|_|=)?([A-Ga-gz])([,']*)(\d*)(/*)(\d*)(-?)|(>)|(\|)")
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

def abc(body, key, unit, tr=0, bar=None):
    """Parse an ABC melody line. unit = beats per L: unit. Returns [(midi|None, beats)]. bar = beats per ABC bar
    (checked: every bar but the first (pickup) and last must be complete)."""
    ks = KEYS[key]; out = []; local = {}; tie = False; broken = False; bars = [0.0]
    for acc, let, octv, n1, sl, n2, tied, brk, bl in TOK.findall(body):
        if bl:
            local = {}; bars.append(0.0); continue
        if brk:
            p, d = out[-1]; out[-1] = (p, d * 1.5); bars[-1] += d * 0.5; broken = True; continue
        d = (int(n1) if n1 else 1) / ((int(n2) if n2 else 2 ** len(sl)) if sl else 1) * unit
        if broken: d *= 0.5; broken = False
        bars[-1] += d
        if let == 'z':
            out.append((None, d)); tie = False; continue
        L = let.upper(); o = 4 if let.isupper() else 5
        o += octv.count("'") - octv.count(',')
        if acc: local[L] = {'^': 1, '_': -1, '=': 0}[acc]
        p = 12 * (o + 1) + STEP[L] + local.get(L, ks.get(L, 0)) + tr
        if tie and out and out[-1][0] == p: out[-1] = (p, out[-1][1] + d)
        else: out.append((p, d))
        tie = bool(tied)
    if bar:
        bars = [b for b in bars if b > 1e-9]
        bad = [i for i, b in enumerate(bars[1:-1], 1) if abs(b - bar) > 1e-6]
        assert not bad, f'incomplete bars {bad}: {[round(bars[i], 3) for i in bad]}'
    return out

def theme(meter, pickup, mel, chords, tr=0, per=1):
    """chords given per ABC bar in the source key; per = ABC bars per suite bar (2 for 6/8 -> 4/4 pairs) or
    -n for one ABC bar spanning n suite bars (Silent Night 6/8 -> two 3/4 bars)."""
    if per > 1:
        chords = ['|'.join(dict.fromkeys(chords[i:i + per])) for i in range(0, len(chords), per)]
    elif per < 0:
        chords = [c for c in chords for _ in range(-per)]
    th = cs.transpose(dict(meter=meter, pickup=pickup, chords=chords), tr)
    L = len(chords) * meter; tot = sum(d for _, d in mel)
    assert tot <= pickup + L + 1e-6, f'melody {tot} > pickup {pickup} + {L}'
    if tot > L + 1e-6:          # last note would overlap the next chorus's pickup
        p, d = mel[-1]; mel = mel[:-1] + [(p, d - (tot - L))]
    th['mel'] = mel
    return th

# Silent Night (Gruber 1818), 6/8 L:1/8 read as 3/4 hymn time (one eighth = one beat), C -> F
SN_ABC = ('G>A G E3|G>A G E2z|d2 d B3|c2 c G2z|A2 A c>B A|G>A G E2z|A2 A c>B A|G>A G E2z|'
          'd2 d f>d B|c3 e2z|cGE G>F D|C3-C3|')
SN_CH = ['C6|C6', 'C6|Dm7', 'G7', 'C6|Am7', 'F6', 'C6', 'F6', 'C6|A7', 'Dm7|G7', 'C6|C6', 'C6|G7', 'C6']
def silent_night(tr): return theme(3, 0, abc(SN_ABC, 'C', 1, tr, 6), [c for x in SN_CH for c in (x.split('|') * 2)[:2]], tr)

THEMES = {}
THEMES['silent_night'] = silent_night(5)

# O Christmas Tree (trad., AABA), D -> Bb
OCT_A = 'D3/4D/4 D E|F3/4F/4 F3/2F/2|E/2F/2 G C|E D '
THEMES['o_christmas_tree'] = theme(3, 1, abc('A,|' + OCT_A + 'A,|' + OCT_A + 'z/2A/2|A/2F/2 B3/2A/2|A/2G/2 G3/2G/2|'
    'G/2E/2 A3/2G/2|G/2F/2 F A,|' + OCT_A + 'z|', 'D', 1, 8, 3),
    ['D6', 'D6', 'Em7|A7', 'D6'] * 2 + ['D6', 'A7', 'Em7|A7', 'D6'] + ['D6', 'D6', 'Em7|A7', 'D6'], 8)

# The First Noel (trad.), D -> F
FN_V = 'D3/2 E/F/G/|A2 B/c/|d c B|A2 B/c/|d c B|A B c|d A G|F2 '
THEMES['first_noel'] = theme(3, 1, abc('F/E/|' + FN_V + 'F/E/|' + FN_V + 'F/E/|D3/2 E/F/G/|A2 d/c/|B2 B|A3|d c B|A B c|d A G|F2 z|',
    'D', 1, 3, 3),
    ['D6', 'D6', 'Gmaj7', 'D6', 'Gmaj7', 'Em7|A7', 'D6|A7', 'D6'] * 2 + ['D6', 'F#m7', 'Gmaj7', 'D6', 'Gmaj7', 'Em7|A7', 'D6|A7', 'D6'], 3)

# Deck the Halls (Welsh trad.), D -> F
DH_A = 'A3 G F2 E2|D2 E2 F2 D2|EFGE F3 E|D2 C2 D4|'
THEMES['deck_the_halls'] = theme(4, 0, abc(DH_A + DH_A + 'E3 F G2 E2|F3 G A2 E2|FG A2 Bc d2|c2 B2 A4|A3 G F2 E2|D2 E2 F2 D2|BBBB A3 G|F2 E2 D4|',
    'D', 0.5, 3, 4),
    ['D6', 'Bm7', 'Em7|D6', 'A7|D6'] * 2 + ['Em7', 'D6|A7', 'D6|Bm7', 'E7|A6', 'D6', 'Bm7', 'Gmaj7|D6', 'A7|D6'], 3)

# Jingle Bells (Pierpont 1857), G -> Bb
THEMES['jingle_bells'] = theme(4, 0, abc(
    'DB AG|D3 D/D/|DB AG|E4|Ec BA|F3 z/F/|dd cA|B3 z/D/|DB AG|D3 z/D/|DB AG|E3 z/E/|Ec BA|dd dd|ed cA|G2 d2|'
    'BB B2|BB B2|Bd G3/2A/2|B4|cc c3/2c/2|cB BB/B/|BA AB|A2 d2|BB B2|BB B2|Bd G3/2A/2|B4|cc c3/2c/2|cB BB/B/|dd cA|G2 z2|',
    'G', 1, 3, 4),
    ['G6', 'G6', 'G6', 'Cmaj7', 'Am7', 'D7', 'D7', 'G6', 'G6', 'G6', 'G6', 'Cmaj7', 'Am7', 'G6', 'D7', 'G6|D7',
     'G6', 'G6', 'G6', 'G6', 'C6', 'G6', 'A7', 'D7', 'G6', 'G6', 'G6', 'G6', 'C6', 'G6', 'D7', 'G6'], 3)

# We Wish You a Merry Christmas (English trad.), G -> C
THEMES['we_wish_you'] = theme(3, 1, abc('D2|G2 GAGF|E2 C2 E2|A2 ABAG|F2 D2 D2|B2 BcBA|G2 E2 DD|E2 A2 F2|G4 D2|'
    'G2 G2 G2|F4 F2|G2 F2 E2|D4 A2|B2 AA G2|d2 D2 DD|E2 A2 F2|G6|', 'G', 0.5, 5, 3),
    ['G6', 'C6', 'A7', 'D7', 'B7', 'Em7', 'Cmaj7|D7', 'G6', 'G6', 'D7', 'A7', 'D7', 'G6', 'D7', 'Cmaj7|D7', 'G6'], 5)

# God Rest Ye Merry, Gentlemen (English trad.), E minor -> G minor
GR_A = 'E B B A|G F E D|E F G A|'
THEMES['god_rest_ye'] = theme(4, 1, abc('E|' + GR_A + 'B3 E|' + GR_A + 'B2 z B|c A B c|d e B A|G E F G|A2 G A|B2 c B|B A G F|'
    'E2 G/F/ E|A2 G A|B c d e|B A G F|E3 z|', 'G', 1, 3, 4),
    ['Em7', 'Em7', 'Cmaj7', 'B7', 'Em7', 'Em7', 'Cmaj7', 'B7', 'Am7', 'G6', 'Em7', 'D7', 'G6', 'B7', 'Em7', 'D7', 'G6', 'B7', 'Em7'], 3)

# Away in a Manger (Kirkpatrick 1895), F -> Bb
THEMES['away_in_a_manger'] = theme(3, 1, abc('c|c3/2 B/ A|A3/2 G/ F|F E D|C2 C|C3/2 D/ C|C G E|D C F|A2 c|c3/2 B/ A|A3/2 G/ F|'
    'F E D|C2 C|B3/2 A/ G|A G F|G D E|F2|', 'F', 1, 5, 3),
    ['F6', 'F6', 'Gm7|C7', 'F6', 'C7', 'C7', 'Gm7|F6', 'F6', 'F6', 'F6', 'Gm7|C7', 'F6', 'Bb6', 'F6', 'Gm7|C7', 'F6'], 5)

# O Holy Night (Adam 1847), 6/8 L:1/8: one dotted quarter = one beat, two 6/8 bars per 4-beat bar, D
OHN = ('F3 F2 F|A3- A2 A|B2 B G2 B|d6|A2 A F2 E|D3 F2 G|A3 G2 E|D6-|D4 z2|'
       'F3 F2 F|A3- A2 A|B2 B G2 B|d6|A2 A ^G2 F|c3 A2 B|c3 d2 c|F6-|F3 z2A|'
       'A3 B3|E3 A3|B2 A d2 F|B3 A2 A|A3 B3|E3 A3|B2 A d2 F|A3- A2 z|'
       'd6-|d2 z c2 B|c6-|c2 z c3|e6-|e z B B2 B|d6-|d3 z2 d|'
       'f6|e3- e2 A|d6-|d2 z c2 B|A6-|A z A B2 A|A6-|A2 z d3|'
       'e6-|e2 z A3|f6-|f3 e3|d3- d2 z|c3 d2 e|d6-|d4 z2|')
THEMES['o_holy_night'] = theme(4, 0, abc(OHN, 'D', 1 / 3, 0, 2),
    ['D6', 'D6', 'Gmaj7', 'D6', 'D6', 'D6', 'A7', 'D6', 'D6',
     'D6', 'D6', 'Gmaj7', 'D6', 'E7', 'F#m7', 'C#7', 'F#m7', 'F#m7',
     'A7', 'A7', 'D6', 'D6', 'A7', 'A7', 'D6', 'D6',
     'Bm7', 'Bm7', 'F#m7', 'F#m7', 'Em7', 'Em7', 'Bm7', 'Bm7',
     'D6', 'A7', 'D6', 'Gmaj7', 'D6', 'A7', 'D6', 'D6',
     'A7', 'A7', 'D6', 'A7', 'D6', 'A7', 'D6', 'D6'], 0, per=2)

# Hark! The Herald Angels Sing (Mendelssohn 1840), F -> Ab
THEMES['hark'] = theme(4, 0, abc('C F F3/2 E/|F A A G|c c c3/2 B/|A G A2|C F F3/2 E/|F A A G|c G G3/2 E/|E D C2|'
    'c c c F|B A A G|c c c F|B A A G|d d d c|B A B2|G A/B/ c3/2 F/|F G A2|d3/2 d/ d c|B A B2|G A/B/ c3/2 F/|F G F2|',
    'F', 1, 3, 4),
    ['F6', 'F6|C7', 'F6|Gm7', 'C7|F6', 'F6', 'Dm7|G7', 'C6', 'G7|C6', 'F6', 'Gm7|C7', 'F6', 'Gm7|C7',
     'Bb6', 'Gm7', 'Gm7|F6', 'C7|F6', 'Bb6', 'Gm7', 'Gm7|F6', 'C7|F6'], 3)

# Angels We Have Heard on High (French trad., Gloria refrain), F -> G
AW_V = 'A A A c|c3/2 B/ A2|A G A c|A3/2 G/ F2|'
AW_R = 'c2 d/c/B/A/|B2 c/B/A/G/|A2 B/A/G/F/|G3/2 C/ C2|F G A B|A2 G2|'
THEMES['angels_we_have_heard'] = theme(4, 0, abc(AW_V * 2 + AW_R * 2 + 'F4|', 'F', 1, 2, 4),
    ['F6', 'C7|F6', 'F6', 'C7|F6'] * 2 + ['F6|Dm7', 'Gm7|C7', 'F6|Bb6', 'C7', 'F6|Bb6', 'C7'] * 2 + ['F6'], 2)

# Good King Wenceslas (Piae Cantiones 1582), G -> A
GK_A = 'G G G A|G G D2|E D E F|G2 G2|'
THEMES['good_king_wenceslas'] = theme(4, 0, abc(GK_A * 2 + 'd c B A|B A G2|E D E F|G2 G2|D D E F|G G A2|d c B A|G2 c2|G4|',
    'G', 1, 2, 4),
    ['G6', 'G6', 'Cmaj7|D7', 'G6'] * 2 + ['G6', 'Em7', 'Cmaj7|D7', 'G6', 'D7', 'G6|D7', 'G6', 'Em7|C6', 'G6'], 2)

# Jolly Old Saint Nicholas (American trad., 1860s), 2/4 pairs as 4/4, Bb -> C
JO_A = 'd/d/d/d/ c/c/c|B/B/B/B/ d2|G/G/G/G/ F/F/B|'
THEMES['jolly_old_saint_nicholas'] = theme(4, 0, abc(JO_A + 'A/B/c/d/ c2|' + JO_A + 'c/B/c/d/ B2|', 'Bb', 1, 2, 4),
    ['Bb6|F7', 'Gm7|Dm7', 'Eb6|Bb6', 'F7', 'Bb6|F7', 'Gm7|Dm7', 'Eb6|Bb6', 'F7|Bb6'], 2)

# Carol of the Bells: Leontovych's Shchedryk (1916) four-note ostinato, G minor
THEMES['carol_of_the_bells'] = theme(3, 0, abc('B A/B/ G|' * 16, 'Gm', 1, 0, 3),
    ['Gm7', 'Gm7', 'Ebmaj7', 'Ebmaj7', 'Cm7', 'Cm7', 'Ebmaj7', 'Gm7', 'Gm7', 'Gm7', 'Cm7', 'Cm7', 'Ebmaj7', 'Ebmaj7', 'Cm7', 'Gm7'], 0)

THEMES['silent_night_eb'] = silent_night(3)

# ------------------------------------------------------------------ arrangement
class Track(cs.Song):
    def __init__(self, theme, seed, bpm):
        super().__init__(bpm, theme['meter'], seed)
        self.theme = theme; self.mel = []
        self.L = len(theme['chords']) * theme['meter']
    def lead(self, t, n, v, d, jitter=0.01):
        self.add('piano', t, n, v, d, jitter); self.mel.append((t, t + d, n))

def melody(s, start, vel, grace=0.0, celesta=False):
    """Carol as written, straight eighths. grace (variations only): a short grace note from below into long notes."""
    th = s.theme; t = start - th['pickup']
    for n, b in th['mel']:
        if n is not None:
            v = vel + (4 if b >= 2 else 0) + s.rng.randint(-3, 3)
            if grace and b >= 2 and s.rng.random() < grace:
                s.add('piano', t - 0.12, n - 1, v - 14, 0.12, 0.0)
            s.lead(t, n, v, b * 0.95)
            if celesta: s.add('celesta', t, n, v - 16, b * 0.9, 0.006)
        t += b

def sleigh(s, start, nbars, vel=34):
    """Very soft sleigh-bell shake: every beat, offbeat eighths lighter."""
    M = s.meter
    for i in range(nbars * M * 2):
        s.add('sleigh', start + i * 0.5, 60, (vel if i % 2 == 0 else vel - 12) + s.rng.randint(-3, 3), 0.4, 0.01)

PATTERN = 'BCSGCBSGC'

def build_track(th, seed, bpm, celesta, bells):
    s = Track(th, seed, bpm); t = th['pickup']; nbars = len(th['chords'])
    chorus = s.L * 60 / bpm
    n = max(2, round((TARGET - 8) / chorus))
    form = 'A' + PATTERN[:n - 2] + 'O' if n > 2 else 'AB'      # long carols: as written, then one brushed chorus
    for sec in form:
        if sec in 'ABCGO':
            melody(s, t, 60 + (2 if sec in 'BC' else 0), grace=0.5 if sec == 'G' else 0, celesta=celesta and sec == 'A')
        if sec == 'S': ep3.solo(s, t, 58)
        ep3.comp(s, t, 'pad' if sec in 'AO' else 'beat', 34 if sec in 'AO' else 35)
        ep3.bass(s, t, 'walk' if sec in 'CGS' else 'two', 84 if sec != 'A' else 80)
        if sec != 'A': ep3.brushes(s, t, nbars, 0.7 if sec == 'O' else 0.9)
        if bells and sec in 'BCG': sleigh(s, t, nbars)
        t += s.L
    ep3.ending(s, t)
    return s, form

TRACKS = {   # id: (title, theme, bpm, seed, celesta on first chorus, sleigh bells)
    '01_silent_night': ('Silent Night', 'silent_night', 96, 11, True, False),
    '02_o_christmas_tree': ('O Christmas Tree', 'o_christmas_tree', 104, 21, False, False),
    '03_the_first_noel': ('The First Noel', 'first_noel', 100, 31, True, False),
    '04_deck_the_halls': ('Deck the Halls', 'deck_the_halls', 112, 41, False, False),
    '05_jingle_bells': ('Jingle Bells', 'jingle_bells', 118, 51, False, True),
    '06_we_wish_you': ('We Wish You a Merry Christmas', 'we_wish_you', 108, 61, False, False),
    '07_god_rest_ye': ('God Rest Ye Merry, Gentlemen', 'god_rest_ye', 104, 71, False, False),
    '08_away_in_a_manger': ('Away in a Manger', 'away_in_a_manger', 96, 81, True, False),
    '09_o_holy_night': ('O Holy Night', 'o_holy_night', 92, 91, False, False),
    '10_hark': ('Hark! The Herald Angels Sing', 'hark', 104, 101, False, False),
    '11_angels_we_have_heard': ('Angels We Have Heard on High', 'angels_we_have_heard', 100, 111, True, False),
    '12_good_king_wenceslas': ('Good King Wenceslas', 'good_king_wenceslas', 108, 121, False, False),
    '13_jolly_old_saint_nicholas': ('Jolly Old Saint Nicholas', 'jolly_old_saint_nicholas', 112, 131, False, True),
    '14_carol_of_the_bells': ('Carol of the Bells', 'carol_of_the_bells', 112, 141, False, False),
    '15_silent_night_reprise': ('Silent Night (Reprise)', 'silent_night_eb', 92, 151, True, False),
}
CREDIT = {'silent_night': 'Gruber, 1818', 'o_christmas_tree': 'trad.', 'first_noel': 'trad.', 'deck_the_halls': 'Welsh trad.',
          'jingle_bells': 'Pierpont, 1857', 'we_wish_you': 'English trad.', 'god_rest_ye': 'English trad.',
          'away_in_a_manger': 'Kirkpatrick, 1895', 'o_holy_night': 'Adam, 1847', 'hark': 'Mendelssohn, 1840',
          'angels_we_have_heard': 'French trad.', 'good_king_wenceslas': 'Piae Cantiones, 1582',
          'jolly_old_saint_nicholas': 'American trad.', 'carol_of_the_bells': 'Leontovych, 1916', 'silent_night_eb': 'Gruber, 1818'}

# ------------------------------------------------------------------ render + mix (EP3 chain + celesta/sleigh)
SLEIGH_SFZ = os.path.join(WORK, 'sleigh.sfz')
SFZ = dict(cs.SFZ, sleigh=SLEIGH_SFZ)
GAIN = dict(ep3.GAIN, celesta=4, sleigh=2)
FILT = dict(ep3.FILT, celesta='highpass=f=200,highshelf=f=6000:g=-5',
            sleigh='highpass=f=1500,highshelf=f=9000:g=-5,pan=stereo|c0=0.75*c0+0.25*c1|c1=0.4*c0+0.6*c1')

def write_sleigh():
    regs = ''.join(f'<region> sample={f} seq_length=3 seq_position={i + 1}\n'
                   for i, f in enumerate(['sleighbell1_hit_quiet.wav', 'sleighbell1_hit_1.wav', 'sleighbell1_hit_2.wav']))
    with open(SLEIGH_SFZ, 'w') as fh:
        fh.write(f'<control> default_path={MISC}\\\n<global> lokey=0 hikey=127 pitch_keycenter=60 ampeg_release=0.4 amp_veltrack=40 volume=12\n' + regs)

def build(tid):
    title, key, bpm, seed, cel, bells = TRACKS[tid]
    s, form = build_track(THEMES[key], seed, bpm, cel, bells)
    d = os.path.join(WORK, tid); os.makedirs(d, exist_ok=True)
    parts = sorted(s.ev)
    for p in parts:
        cs.write_midi(s, p, os.path.join(d, p + '.mid'))
        cs.run([cs.SFIZZ, '--sfz', SFZ[p], '--midi', os.path.join(d, p + '.mid'), '--wav', os.path.join(d, p + '.wav'),
                '-s', '48000', '-q', '3', '-p', '256'])
    dur = s.length() * 60 / bpm + 3
    ins, fc = [], []
    for i, p in enumerate(parts):
        ins += ['-i', os.path.join(d, p + '.wav')]
        fc.append(f'[{i}:a]{FILT[p]},volume={GAIN[p]}dB[s{i}]')
    ins += ['-i', cs.IR]; k = len(parts)
    fc.append(''.join(f'[s{i}]' for i in range(k)) + f'amix=inputs={k}:normalize=0:duration=longest,atrim=0:{dur:.2f},asplit[dry][send]')
    fc.append('[send]highpass=f=200,lowpass=f=6000[sendf]')
    fc.append(f'[sendf][{k}:a]afir=dry=10:wet=10:length=1,volume=-10dB[wet]')
    fc.append(f'[dry][wet]amix=inputs=2:normalize=0:duration=first,lowpass=f=14000,afade=t=out:st={dur - 4:.2f}:d=4')
    out = os.path.join(WORK, tid + '.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-ar', '48000', '-c:a', 'pcm_f32le', out])
    assert ep3.nan_free(out), 'NaN samples in ' + out
    print(tid, f'{dur:.1f}s', bpm, 'bpm', form, flush=True)

def join():
    ids = list(TRACKS); files = [os.path.join(WORK, t + '.wav') for t in ids]
    ins = sum([['-i', f] for f in files], [])
    fc = [f'[{i}:a]volume={-20 - ep3.lufs(f):.2f}dB[n{i}]' for i, f in enumerate(files)]
    cur = '[n0]'
    for i in range(1, len(files)):
        fc.append(f'{cur}[n{i}]acrossfade=d=4:c1=tri:c2=tri[x{i}]'); cur = f'[x{i}]'
    pre = os.path.join(WORK, 'suite_premaster.wav')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', cur, '-c:a', 'pcm_f32le', pre])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-17:TP=-1.5:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    js = json.loads(r[r.rindex('{'):r.rindex('}') + 1]); g = -17 - float(js['input_i'])
    base = os.path.join(OUT, 'you_elsewhere_ep04_christmas_suite')
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', pre, '-af', f'volume={g:.2f}dB,alimiter=limit=0.84:attack=4:release=60:level=false',
            '-ar', '48000', '-c:a', 'pcm_s24le', base + '.wav'])
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-c:a', 'libmp3lame', '-b:a', '256k', base + '.mp3'])
    cs.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base + '.wav', '-t', '90', '-af', 'afade=t=out:st=86:d=4',
            '-c:a', 'libmp3lame', '-b:a', '256k', os.path.join(OUT, 'you_elsewhere_ep04_christmas_first90s.mp3')])
    t = 0.0; lines = []
    for tid, f in zip(ids, files):
        title, key, *_ = TRACKS[tid]
        mm, ss = divmod(int(round(t)), 60)
        lines.append(f'{mm}:{ss:02d} {title} ({CREDIT[key]})')
        t += ep3.duration(f) - 4
    total = ep3.duration(base + '.wav')
    with open(os.path.join(OUT, 'tracklist.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + f'\n\n(total {int(total // 60)}:{int(total % 60):02d})\n'
                 'All melodies public domain; arrangements and recordings original.\n')
    print('\n'.join(lines)); print('total', round(total, 1), 's, gain', round(g, 2))

if __name__ == '__main__':
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True); write_sleigh()
    todo = sys.argv[1:] or list(TRACKS)
    for tid in todo: build(tid)
    if not sys.argv[1:]: join()
