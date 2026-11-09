# EP08 Conjuring Universe shot list, read by build_edl.py (cloud skeleton 11/9 KST from beats_v1.md). One list for both scripts:
# pick() takes the v1.1 shots when the take holds the v1.1 wording (script_v1_1.md, no film files) and the v1 shots otherwise.
# A shot is (phrase, clip, in_s, -clean_s[, opts]): it starts 0.08 s before the first word of the exact script phrase and runs until
# the next shot. in_s = the in-point in the clip, -clean_s = seconds of clean picture from the in-point (no cut to another scene, no
# text, logo or end card); the builder slows a shot (never below 0.4x) when the clean span is shorter than its slot.
# Every span below comes from the laptop's frame-checked beat map (beats_v1.md); "(verify)" marks a span taken from a clip summary
# that was not frame-checked yet. On the laptop (Phase B): confirm each in-point on real frames, keep each comment true to what is on
# screen, and replace every TODO/GAP shot (film file, age-gated clip, or the v1.1 rewording) before rendering: a TODO is skipped and
# the previous shot runs on, which would be a silent substitute (owner rule: never).
# Framing:  L   subject left of the stat card (the card covers x 840-1920 from the card phrase to the section end; in s01 from 0)
#           AR  The Conjuring Archives uploads: zoom 1.38 crops the letterbox bars, which carry that channel's logo (never cover it)
#           Creation Movieclips clips are full frame with the mark ON the picture: shots_grade.py CLIPOPT top-anchors a 1.13 zoom so the
#           mark stays out of frame (build_edl.py warns when any listed mark is visible and not under a black bottom bar)
# opts: z, dx, dy (px), flip=1, g (gamma), a (clip audio dB), lufs (levelled clip audio), f=<film key> (label for the mixed clip 'universe')
# Inserts: ins(after_phrase, seconds, 'film', shots=[(0, clip, in, 1.0, opts)], sub='exactly as spoken'), in = 0.25 s before the first
# word, seconds = line length + 0.35 s, opts 'lufs=-17'. Each insert sits before the entry's card phrase (build_edl.py warns otherwise).
TODO = None
L = 'z=1.35,dx=249'
AR = 'z=1.38'
ARL = 'z=1.38,dx=249'
def o(*a): return ','.join(x for x in a if x)
def said(seg, phrase):   # which script was voiced: v1 (with the owner's film files) or v1.1 (script_v1_1.md, no film files)
    try: find(seg, phrase); return True
    except KeyError: return False
def pick(seg, phrase, v11, v1):   # the shots of whichever wording the take holds
    return v11 if said(seg, phrase) else v1
C1, C2, DM = 'f=c1', 'f=c2', 'f=dm'   # film keys for the mixed WB compilation 'universe' (Conjuring 2013 0-936, Conjuring 2 938-1556, DMMDI 1558-1816)

# ---- s00 cold open: one hard cut per caption, the caption's action on screen from the shot's first frame (owner 11/7) ----
X.append(sec('s00', [
  (0, 'c2_painting', 136.97, -1.7),  # 136.5-136.93 is a dark, barely visible Valak face from the previous shot (hard cut at 136.95); the bright face runs 136.97-138.70. s04 'survival rate' c2_painting 137.2-138.8 is now the same moment: s04 needs another span
  ('will burn you alive', 'co_burn_4k', 157.5, -0.7, 'a=-18'),  # Father Noiret burning, his head and arms inside the flames; hard cut at 158.2 to an all-fire shot (the old span crossed it)
  ('in midair', 'co_burn_4k', 154.9, -1.1),  # cut at 156.03 to a boy in the pews
  ('bury you alive', 'co_buried_b', 102.4, -3.4),  # one shot 99.5-105.85, but the lighter is only lit from ~102.4 (100-102 is near-black)
  ('snap your neck', 'n2_deliv', 137.8, -0.6, 'a=-16,g=1.4'),    # The Nun II: the delivery girl screams as Valak lifts her (cut before her feet at 138.5)
  ('make you stab', 'dm_vision', 153.15, -0.85, o(AR, 'g=1.4')),  # 153.0-153.1 is an arm only; the bloody knife is in frame from 153.15; cut to Jessica at 154.05
  ('your best friend', 'dm_vision', 160.0, -0.85, o(AR, 'g=1.25')),  # cut to Lorraine at 160.89
  ('twenty-two times', 'dm_vision', 157.1, -1.8, o(AR, 'g=1.25')),  # 156.7-157.0 her eyes are down; the white eyes show from 157.1; cut to Lorraine at ~159.0
  ('or turn your own mother', 'co_mother_c', 305.9, -5.1, 'g=1.4'), # The Conjuring: possessed Carolyn's grinning face next to Roger
  ('against you', 'universe', 659.1, -1.8, C1),            # possessed Carolyn raising the scissors in the crawlspace, going for April
  ('and sometimes', 'universe', 904.0, -1.5, C1),          # the Annabelle doll close-up (The Conjuring's prologue)
  ('all it takes', 'ach_devil_cz', 297.5, -0.7),           # Annabelle Comes Home: the whole doll seated in the open glass case
  ('is a doll', 'cr_wheel', 535.9, -8.7),                  # Annabelle: Creation: the doll in a carved chair, daylight, sharp, centred
  ("we're ranking", 'still_posterwall', 0.0, -5.0),        # the 9 posters pop in (release order) and hold to the end
  ], extra=[('word', w, a, b) for w, a, b in [
    ('These demons', 0, 'will burn you alive'),
    ('Will burn you alive', 'will burn you alive', 'in midair'),
    ('In midair', 'in midair', 'bury you alive'),
    ('Bury you alive', 'bury you alive', 'snap your neck'),
    ('Snap your neck', 'snap your neck', 'make you stab'),
    ('Make you stab', 'make you stab', 'your best friend'),
    ('Your best friend', 'your best friend', 'twenty-two times'),
    ('22 times', 'twenty-two times', 'or turn your own mother'),
    ('Or turn your own mother', 'or turn your own mother', 'against you'),
    ('Against you', 'against you', 'and sometimes'),
    ('And sometimes', 'and sometimes', 'all it takes'),
    ('All it takes', 'all it takes', 'is a doll'),
    ('Is a doll', 'is a doll', "we're ranking"),
    ("We're ranking", "we're ranking", 'every conjuring demon'),
    ('Every Conjuring demon', 'every conjuring demon', 'by your chance'),
    ('By your chance', 'by your chance', 'of surviving it'),
    ('Of surviving it', 'of surviving it', 999),
  ]], clip_db=-22))
def fr(t): return max(0.0, round(t * 30) / 30 - 0.005)   # frame-exact: a caption starts on its cut's own frame and ends where the next begins
for ov in X[-1]['overlays']:   # captions flash and cut out (one word 0.9 s, a phrase 1.6 s max); the frame-0 caption holds to its cut
    if ov[0] == 'word':
        b = ov[3] if ov[2] == 0 else min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.6))
        ov[2], ov[3] = (fr(ov[2]) if ov[2] > 0 else 0.0), (fr(b) if b < 900 else b)
X[-1]['vfade'] = {'out': 0.2}

# ---- s01 rules: the demo card covers the right half from frame 0, so every shot keeps its subject left (L) ----
X.append(sec('s01', [
  (0, 'ach_room', 44.0, -8.0, 'z=1.35'),  # Daniela standing among the artifacts, wide and dark (one slow push-in 36-52.3). 10-12.4 and 12.5-23 were two shots; with L, Daniela was cropped off the left edge, while dx=0 puts her at out x 150-400
  ('comes for you', 'n2_deliv', 126.2, -3.2, L),           # Valak in the nun habit at the end of a hallway that turns red
  ('and every one is different', 'c2_grave', 118.82, -5.2, 'z=1.5,dx=320'),  # 118.0-118.78 is Bill Wilkins's ghost (another shot); Janet on the sofa 118.8-124.1. At L her face sat on x 840; z 1.5 dx 320 moves it to out x ~0-420
  ("one can't touch you", 'ach_devil_cz', 298.32, -1.3, 'z=1.35,dx=-249,g=1.4'),  # TODO filled: Judy's hand on the shut glass, Annabelle (red rose) inside; one shot 298.3-299.65. Judy is at out x 0-700 and the doll sits under the card. 300.0 itself is a dark wide shot (cut 299.7, next cut 300.7)
  ('one needs you to hand', 'a14_baby', 35.88, -1.4, 'z=1.35,dx=-249'),  # the 2nd angle of "her SOUL" on the ceiling (cut in 35.86, out ~37.35), so s03 keeps 58.7 alone. dx=-249 keeps the word left of 840 (at L it was cropped or under the card)
  ('and one has wiped out', 'co_valak0', 93.0, -1.2, o(L, 'g=1.25')),
  ('an entire abbey', 'n1_pray', 2.15, -1.85, o(L, 'g=1.4')),  # cut to Irene at ~94.2. Valak's face at out x ~600. co_valak0's picture is rows 140-939 (measured at 30.5/88/93.5), not 266-901, so L (rows 140-940) fills the frame with no bars
  ('so we score', 'lr_end', 46.0, -2.8, L),  # Last Rites: Ed walks in fast, left of 840, Lorraine behind him (under the card); cut at ~48.9
  ('strength', 'co_mother_c', 240.0, -3.4, L),             # The Conjuring: Carolyn levitating in the chair under the sheet
  ('intelligence', 'dm_altar', 128.0, -3.5, o(ARL, 'g=1.25')),  # (verify) resolved: DMMDI, the Occultist standing behind her candle-lit altar table (one shot 125-131.9, her at out x ~380). 118 is black; 119-124.5 is a woman walking in, back to camera
  ('kill count', 'cr_wheel', 567.12, -1.6, o(L, 'g=1.25')),  # Creation: Samuel's body on the floor, wide (567.07-568.77). The old span was the nun's reaction (568.8-571), then the CLOSE upside-down dead face (571-573) and the ClipZone end card (573.2): not usable
  ('and possession', 'lr_end', 99.43, -2.42, L),  # possessed Judy's bloody grin, close, warm light. 108.9 is another shot, 108.97-109.13 a bright 0.17 s shot, and the grin shot runs 109.15-109.58, then a cut to a crying face
  ('take over your body', 'dm_david', 315.93, -1.3, o(L, 'flip=1')),  # 232-238 had 3 cuts (hand/Janet, Lorraine and Hodgson, crucifix). Possessed Janet's screaming face behind the wall boards is one shot 220.35-221.45; z 1.6 dx 360 puts it at out x ~640
  ('put it all together', 'spooky_nun', 1112.0, -2.9, L),  # cut to an empty corridor at 1114.98
  ]))
X[-1]['vfade'] = {'in': 0.2}

# ---- s02 #9 Annabelle Comes Home (95%) ----
X.append(sec('s02', [
  (0, 'ach_room', 36.3, -7.5),  # same push-in shot (36-52.3); s01 now takes 44-52, so s02 ends at 43.8 (no moment twice)
  ('this annabelle', 'ach_case', 62.0, -1.85),  # ach_devil_cz 316.4-317.9 is the SAME footage as ach_end 92.9-94.4 (row 'and as long as'; ClipZone ach_devil_cz = Movieclips ach_end + 223.5 s). Now: the Annabelle doll sitting still in the car, dark (one shot 61.9-63.95; MC clip, bar)
  ("because it's locked", 'ach_end', 57.8, -0.7),  # 57.7 is mid-whip (blur); the still doll in the case runs 57.75-58.55
  ('a blessed glass case', 'ach_end', 53.6, -1.6),  # 285.0-288.4 = ach_end 61.5-64.9, which 'leave the glass shut' uses. Now: Mary Ellen's hand flat on the case glass, the card taped on it (one shot 53.55-55.25)
  ("in the warrens' room", 'ach_room', 244.0, -4.0),       # "DANGER! DO NOT TOUCH ANYTHING!" sign, pull back to the WARRENS DEMONOLOGY WITCHCRAFT door
  ('and as long as', 'ach_end', 92.9, -1.5),
  ("it can't touch anyone", 'ach_room', 23.65, -4.6, 'g=1.4'),               # Daniela in the artifact room, Annabelle in the case behind her
  *pick('s02', 'lets the doll out', [
    ('when a teenager sneaks in', 'ach_room', 55.0, -3.0, 'g=1.25'),  # (verify) resolved: 54.0 is the end of the wide shot; Daniela alone, close on her face, 54.6-58+
    ('and lets the doll out', 'ach_hands', 32.05, -2.3, 'g=1.4'),  # Annabelle under the sheet in Judy's bed 32.0-34.4; cut to Judy's face at 34.45 (32-37 held 3 cuts)
  ], [('when a teenager opens', 'GAP', TODO, TODO)]),       # v1 GAP: Daniela opening the case (in no clip): the film file
  ('it wakes up everything', 'ach_room', 236.6, -0.9),     # a burned-face spirit lunges in the artifact room
  ('in that room', 'ach_tv', 26.0, -18.0),                 # the haunted TV showing Daniela
  ('the ferryman', 'ach_ferry_b', 70.5, -2.5, 'g=1.4'),             # the Ferryman's coin-eyed face lit by the lantern (dark)
  ('the babysitter', 'ach_ferry_b', 64.0, -3.8),           # Mary Ellen with the lantern, searching
  ('the bride takes over', 'ach_devil_cz', 148.2, -1.1),   # Daniela in the bride's veil and dress, standing over Judy in the dark
  ('her friend', 'ach_devil_cz', 150.7, -1.1, 'g=1.4'),             # close: the veiled, possessed Daniela, blank dark-eyed stare
  ('a hellhound attacks', 'ach_wolf', 49.3, -1.0),         # the hellhound's claws through the car window (very dark)
  ('a boy outside', 'ach_wolf', 45.78, -1.1),  # 45.5-45.7 is another dark shot (cut 45.73); Bob screaming in the car 45.75-46.9+
  ('and a board game', 'ach_devil_cz', 196.25, -1.2, 'g=1.4'),  # 195.6-196.2 is a close-up of Judy's feet; cut at 196.22 to Judy sprawled by the Feeley Meeley box (name legible)
  ('with dead hands', 'ach_devil_cz', 199.7, -4.5),        # overhead: grey dead hands reach out of the board and grab Judy's arm
  ('but in the whole movie', 'ach_end', 88.0, -1.8),       # the three girls together, Judy holding the crucifix
  ("and it's beaten by", 'ach_end', 82.4, -2.2),           # Mary Ellen, Daniela and Judy side by side
  ('who simply put the doll', 'ach_end', 77.62, -1.65),  # 74.0-74.75 = ach_devil_cz 297.5-298.2 (s00 'all it takes', same footage). Now: Mary Ellen and Daniela push the glass door shut (77.57-79.3)
  ('and lock it', 'ach_end', 80.3, -0.9),                  # the key turning in the case lock
  ('leave the glass shut', 'ach_end', 61.9, -2.6, L),      # Judy at the glass, Annabelle sitting inside the case
  ('survival rate', 'ach_devil_cz', 317.95, -5.6, L),  # TODO filled: Judy, safe in the artifact room, close (one shot 317.85-323.7, face at out x 0-300). The crucifix fight 46-81 is all 0.5-1 s cuts; a long ACH doll close-up stays a GAP (film file)
  ]))

# ---- s03 #8 Annabelle (2014) (80%) ----
X.append(sec('s03', [
  (0, 'a14_baby', 45.8, -2.2),                             # the Annabelle doll in Leah's crib, top shot
  ('this demon is more', 'a14_fire', 5.8, -2.5, AR),  # TODO filled: Mia at her sewing machine at home, calm, wide (one shot 5.71-8.41)
  ("because it isn't locked", 'a14_basement', 73.0, -1.25),  # cut at 74.28
  ('it lives in the doll', 'a14_baby', 33.45, -2.3),  # TODO filled: Mia in the nursery, low angle under the mobile (33.4-35.83). No shot in a14_baby shows the doll on a shelf: comment changes to that
  ('but it has one big weakness', 'a14_basement', 113.0, -4.6),  # the Annabelle demon/ghost standing at the bright window (the card has the rest)
  ('it needs a soul', 'a14_baby', 58.7, -1.65),  # cut to Mia with the doll at 60.38
  ('so it plays with you', 'a14_basement', 61.0, -2.3),  # cut to Leah at 63.33
  ('starting a fire', 'a14_fire', 87.22, -1.5, AR),  # 86.55-87.17 is a top shot of the stove; the side shot of the foil pan bursting into flame runs 87.19-89.2+
  ('in the kitchen', 'a14_fire', 108.5, -2.2, AR),  # cut at 110.74 to a closer stove shot
  ('chasing you through', 'a14_stairs', 11.8, -1.3),  # 48.5 is black and 48.5-51 holds 6+ flash cuts. Now: Mia running away down the dark storage corridor (11.8-13.15, cut to the caged room at 13.18)
                                                           # 65.0-65.3 can be cut in where a slot allows it)
  *pick('s03', 'then it steals', [], [
    ('and attacking the priest', 'a14_priest', TODO, TODO),  # v1 GAP: age-gated a14_priest (qa/age_gated.txt) or the film file
    ('then it takes over', 'a14_priest', TODO, TODO),        # v1 GAP: the demon in the priest's body (same source)
  ]),
  ("steals mia's baby", 'a14_baby', 55.3, -3.1),                  # Mia pulls the bundle from the crib: it is the doll, not Leah
  ('to force a trade', 'a14_basement', 63.4, -1.35),
  ('the baby for her soul', 'a14_basement', 69.8, -2.9),  # baby Leah on the bed; cut at 64.78 (it does not extend)
  ('in the end', 'a14_baby', 159.2, -2.4, 'g=1.4'),                 # Evelyn (red headscarf) on the stairs (never her fall)
  ('who gives up her own life', 'a14_basement', 126.0, -1.8, 'g=1.4'),  # cut to John at the door at 127.87
  ('never offer it your soul', 'a14_basement', 119.6, -5.75, L),  # the Annabelle demon at the window, close (122.6-125.4), through the % line
  ]))

# ---- s04 #7 The Conjuring (65%) ----
X.append(sec('s04', [
  (0, 'c1_sheets', 22.8, -4.3),  # low-angle farmhouse with the sheet flying off the line (20-22.6 is Lorraine at the line; cut 27.15)
  ('this demon is far', 'c1_sheets', 27.2, -1.8),  # Lorraine stares at the house (cut 29.05)
  ("because it doesn't need", 'c1_sleep', 20.0, -6.0),  # one girl points at the dark gap behind the open door, her sister in bed (one shot; comment only)
  ('bathsheba was a witch', 'co_mother_b', 264.0, -1.35, 'g=1.4'),  # Bathsheba's grey face close (257.5-258.7 is a dark lens, her face only 258.8-259.3)
  ('who gave her own baby', 'co_mother_b', 265.35, -1.35, 'g=1.4'),  # same close-up continues (263.5-263.95 is Lorraine; cut 266.75)
                                                           # the sacrifice itself is only in c1_land under burned subtitles: the film file)
  ('and she curses anyone', 'c1_dog_b', 14.75, -3.5),  # Perrons unloading at the farmhouse (12-14.6 is the car through trees; cut 18.4)
  ('she stops every clock', 'c1_land', 141.0, -4.5),       # the alarm clock stopped at about 3:07 (no subtitle after 140.8)
  ('leaves bruises', 'c1_dog_b', 56.15, -1.05),
  ('while she sleeps', 'c1_dog_b', 57.3, -1.25),  # the bruise on Carolyn's leg (56.0 is the previous shot; cut 57.25)
  ('pulls at the girls', 'c1_sleep', 1.0, -2.3),  # Christine asleep, jerks awake (cut 3.35)
  ('and kills the family dog', 'c1_dog_b', 88.3, -1.0),  # Sadie lying in the weeds by the wall, small (87-87.7 Roger, 87.8-88.25 whip pan; cut 89.35)
  ('then she takes over', 'co_mother_c', 292.2, -1.0, 'g=1.4'),
  ('the mother#2', 'co_mother_c', 300.35, -1.35, 'g=1.4'),  # possessed Carolyn laughing (291.5-292.0 is Roger)
  ('completely', 'universe', 477.5, -2.0, C1),  # Carolyn held down by the men, screaming (476.5-477.45 is Lorraine; cut ~479.55)
  ('because in every family', 'universe', 445.8, -1.35, C1),  # possessed Carolyn with the scissors over the child (444.5-445.7 dark/Ed; cut 447.15)
  ('she makes the mother', 'c1_feed', 99.8, -1.6),  # Carolyn on the floor clutching her head, screaming, held (96-99.7 has 4 cuts; MC bar)
  ('the perrons only survive', 'co_mother_c', 10.0, -5.0), # Ed reads the rite from the book in the cellar
  ('and lorraine reaches', 'universe', 694.2, -1.45, C1),  # Lorraine close, in tears, talking to Carolyn (690.5-691.2 possessed Carolyn, white flash 691.24)
  ('with a happy memory', 'universe', 697.58, -0.58, C1),
  ('memory', 'universe', 698.8, -0.6, C1),  # the mother in red running on the beach with her girl (every beach shot is <=0.6 s; 695.8-697.5 is possessed Carolyn)
  ('she only wants the mother', 'universe', 715.6, -4.0, o(C1, 'z=1.35')),
  ('survival rate', 'co_mother_c', 301.8, -3.75, L),  # Ed's hand on possessed Carolyn's head, she screams: one shot 715.5-719.63 (702-716 had 4 cuts + a family photo 713.2-715.4); dx=0 keeps her face at x 0-560 (L cut it off at the left edge)
  ]))

# ---- s05 #6 The Conjuring 2 (55%): two real film lines from Lorraine ----
X.append(sec('s05', [
  (0, 'universe', 1086.0, -4.95, C2),  # Janet on the sofa, one shot (cut 1091.05; no street in this span)
  ('this is the first time', 'c2_painting', 203.0, -1.9),  # the Valak painting on the wall, Valak pushes out of it 204.5-204.9 (cut 204.95)
  ("and it's much smarter", 'c2_painting', 58.2, -5.0, 'g=1.4'),  # Valak standing in the dark behind Lorraine (58.0 is the previous wide; cut 63.35)
  ('it hides behind', 'c2_vision', 0.0, -11.0),            # Bill Wilkins in his armchair, Lorraine across the room (800p)
  ('so everyone thinks', 'c2_vision', 56.05, -0.7),
  ("it's just a ghost", 'c2_vision', 25.25, -4.25),  # wide: Bill in his chair, Valak's pale face in the dark top-left (55.6-55.95 Bill close; cut 56.78 to Valak close)
  ("it blocks lorraine's visions", 'c2_vision', 12.0, -3.0, 'g=1.4'),  # Lorraine staring, unsettled
  *pick('s05', 'fight his way in', [], [("shows her ed's death", 'GAP', TODO, TODO)]),   # v1 GAP: Lorraine's vision of Ed impaled: the film file
  ('and sends the crooked man', 'c2_crooked', 66.15, -1.45, 'g=1.4'),  # the Crooked Man's shape in the tent (65.8-66.05 is Billy; cut 67.65)
  ('after the youngest boy', 'c2_crooked', 73.95, -1.7, 'g=1.4'),  # the Crooked Man lunges (73.5-73.85 is Billy; cut 75.68)
  ('then it takes over janet', 'c2_janet', 220.3, -1.15),  # possessed Janet grinning in the wall (219.5-220.25 Ed / his arm in the wall; cut 221.45)
  *pick('s05', 'fight his way in', [
    ('and ed has to fight', 'c2_janet', 214.25, -2.05),  # v1.1: Ed and the neighbour with a crowbar at the boarded wall, Ed shoves at it (cuts 214.15, 216.35, 217.15)
  ], [
    ('walks her to a window', 'GAP', TODO, TODO),            # v1 GAP: Janet at the window (never a jump): the film file
    ('and ed nearly dies', 'GAP', TODO, TODO),               # v1 GAP: Ed hanging from the curtain: the film file
  ]),
  ('but valak has one', 'c2_name_b', 12.4, -3.0, AR),  # Lorraine in the pouring rain, looking up (one shot 11.9-19.65; no 2 s bible shot in 0-58)
  ('if you know its name', 'c2_name_b', 58.3, -1.65, AR),  # Lorraine bent over the bible (58.0-58.25 bible cover; cuts 58.28, 59.97; the scrawled pages 60.0-61.05 are only 1 s)
  ('and lorraine sends it back', 'c2_name', 44.0, -3.0, AR),  # Lorraine shouts the name at Valak
  ('learn the name', 'c2_name', 55.85, -1.8, ARL),  # Valak's rotting face before it is pulled back (55.5-55.75 is Lorraine; cut 57.68), left of 840
  ('survival rate', 'c2_painting', 189.6, -4.2, 'z=1.5,dx=320'),  # coordinator: s00 frame 0 now holds 136.97-138.70. Valak's face over Lorraine's shoulder (cut 71.15 / 72.57), face at x 300-820
  ], inserts=[
    ins('you have power over it', 1.97, 'film', shots=[(0, 'c2_name', 39.75, 1.0, o(AR, 'lufs=-17'))], sub='You are Valak.'),
    ins('just by saying it', 2.13, 'film', shots=[(0, 'c2_name', 52.81, 1.0, o(AR, 'lufs=-17'))], sub='I condemn you back to hell.'),
  ]))   # Phase B: check Lorraine is on screen while she speaks in both inserts (else start on the Valak reaction and keep the audio)

# ---- s06 #5 The Conjuring: Last Rites (45%) ----
X.append(sec('s06', [
  (0, 'lr_family', 102.2, -3.95),  # the Smurl street at night, headlights in the fog (101.6-102.17 is the previous shot; cut 106.2 to the duplex)
  ('this demon is stronger', 'lr_end', 42.0, -3.0),        # the ornate mirror on the wall, glowing
  ('than that valak', 'c2_painting', 206.88, -0.75),  # the mirror demon's face, the whole shot is 514.6-515.03
  ('and it came closer', 'lr_exorcism', 55.92, -1.1),  # Lorraine bloodied in the attic (cut 57.1)
  ('to killing the warrens', 'lr_judy', 234.1, -1.9),  # Judy choked by an unseen hand (230-230.6 mirror-room wide; cut 231.97)
  ('it lives inside', 'lr_preview', 184.0, -6.0),          # the mirror hanging in the Smurl dining room
  ('and in nineteen sixty-four', 'lr_birth', 20.05, -10.0, 'g=1.4'),  # 1964: Lorraine in labour, crying (cut at 20.02)
  ('it nearly killed judy', 'lr_birth', 55.3, -2.6),  # Lorraine with the still, wrapped baby, a hand over it (one handheld shot to ~58; 55.0 inside a blur)
  ('twenty-two years later', 'lr_judy', 50.0, -6.5),       # adult Judy in the wedding dress in the mirror room
  ('it uses three ghosts', 'lr_axe', 234.75, -0.42, 'g=1.4'),  # grey ghost face snarling (234.73-235.2)
  ('three ghosts', 'lr_exorcism', 80.8, -2.2),  # the axe man with the lantern, one shot 80.75-83.0+ (64.0 had a cut at 64.15 to Lorraine)
  ('to haunt the smurl family', 'lr_exorcism', 39.4, -3.3, 'g=1.4'),  # the old woman ghost in the attic, dark (38-39.3 is Lorraine; cut 42.78)
  ('drives the priest', 'lr_priest', 31.0, -3.7),  # Father Gordon alone at his desk, wide (29.6-30.8 his profile; cuts 34.8, 37.0)
  ('to his death', 'lr_priest', 138.45, -1.95),  # his eyes behind the glasses, the candle reflected (137.6-138.35 is another shot); ends 140.4, never the hallway
  ('gives ed a heart attack', 'lr_exorcism', 346.3, -0.9),  # Ed on the floor in pain (cut 347.25 to Lorraine)
  ('and takes over judy', 'lr_end', 177.0, -3.0),          # possessed Judy snarling (blood in the mouth, not extreme)
  ("ed's exorcism", 'lr_end', 24.0, -1.5),                 # Ed raises his hand with the bible at the mirror
  ('even work', 'lr_end', 80.8, -1.15),  # the bible bursts into flames in Ed's hand (80.75-81.95); 82.0 was Ed's face then a cut at 82.97
  ('and only the whole family', 'lr_exorcism', 503.7, -2.8),  # hands on the glass, cracks from ~506 (cut 506.55)
  ('can break the mirror', 'lr_exorcism', 513.0, -1.35),  # Lorraine and Judy, the demon screaming in the reflection (cut 514.45)
  ('if it wants you', 'lr_exorcism', 474.6, -2.75, 'z=1.2,dx=160'),  # Lorraine holding Judy (cut 477.4); 480 cut at 482.2 and sat across the card; here Lorraine left, Judy's face at the card edge
  ('survival rate', 'lr_judy', 232.0, -2.0, 'z=1.6,dx=360'),  # 539.4-540.8 is Judy's plain face (ghost only 540.85-541.05); now demonic Judy grinning in the cracked mirror, face x 0-800
  ]))   # lr_end t = lr_exorcism t - 330 (same footage): never use both for one moment

# ---- s07 #4 Annabelle: Creation (40%) ----
X.append(sec('s07', [
  (0, 'cr_sam', 29.3, -7.7),                               # the Annabelle doll in a chair, bright, dead centre
  ('this is where the annabelle', 'cr_wasnt', 0.0, -2.6),  # the doll at a tea table with the girl in Bee's dress
  ('and unlike the last one', 'cr_trapped', 355.5, -1.55),
  ('it kills almost everyone', 'cr_trapped', 357.1, -3.0),  # possessed Janice crouched over Linda on the floor (352-355.45 has 4 cuts; cut 357.05)
  ('it pretends to be bee', 'cr_wasnt', 15.0, -4.5),       # the demon as Bee, walking in Bee's room
  ('so her heartbroken parents', 'cr_wasnt', 39.1, -2.95),  # Esther (half-masked) drinking, then looking up (37.6-38.9 is Samuel; cut 42.1; never 34-36)
  ('let it into the doll', 'cr_wasnt', 60.8, -2.2),        # the doll's face close, sinister
  ('then it goes after', 'cr_sam', 37.8, -5.2),            # Sister Charlotte and the orphans unloading the truck
  *pick('s07', 'drags janice', [
    ('it drags janice', 'cr_wheel', 80.35, -0.8),  # v1.1: unseen hands grip Janice's shoulders (79.34-80.25 wheels + running feet; cut 81.2)
    ('out of her wheelchair', 'cr_wheel', 86.6, -0.9),  # skirt and boots running, pushing the chair (cut 87.6)
    ('into a barn', 'cr_wheel', 94.7, -2.3),                 # Janice thrown from the chair, face down on the barn floor
  ], [
    ('it throws janice', 'cr_soul', 155.0, -2.3),            # v1: Janice riding the stairlift
    ('off her stairlift', 'GAP', TODO, TODO),                # v1 GAP: the throw (cr_soul ends before it): the film file
  ]),
  ('and takes over her body', 'cr_stair', 125.6, -2.0),    # the demon forces itself into Janice's mouth in the barn (end card from ~128)
  ('through her', 'cr_sam', 16.0, -8.0),                   # Samuel holding up the crucifix, his fingers bending back (cut before 26)
  ('and kills him', 'cr_sam', 59.8, -1.2),                 # his body on the floor, wide (never 63-64)
  *pick('s07', 'drags janice', [], [('it kills his wife', 'cr_dumb', TODO, TODO)]),   # v1 GAP: Esther's death (cr_dumb age-gated) or the film file
  ('and twelve years later', 'cr_end', 9.05, -5.95),  # the Higgins photos; the burned "12 YEARS LATER" is still faintly on until ~8.95
  ('it kills the couple', 'cr_end', 19.0, -3.3),  # the Higgins couple woken in bed (cut ~22.45)
  ('who adopted her', 'cr_end', 39.5, -1.9),  # grown Annabelle grabs her father's throat (cut 41.45)
  ('five girls and a nun', 'cr_well', 116.4, -3.2),        # Sister Charlotte holding Linda in the field
  ('but only because they run', 'cr_well', 121.2, -6.6, 'g=1.4'),  # the girls running across the field at night (cut ~121.1)
  *pick('s07', 'stays inside janice', [
    ('and the demon stays', 'cr_trapped', 256.3, -5.5),      # v1.1: possessed Janice in a blue nightgown, a sly demonic smile, holding a doll
  ], [('and the demon walks away', 'GAP', TODO, TODO)]),    # v1 GAP: Janice leaving the orphanage: the film file
  ("if you're the weakest", 'cr_soul', 140.6, -7.8, 'z=1.2,dx=-160'),  # Janice scared on the dark landing; at L her face was cut by the left edge, here x 0-800
  ('survival rate', 'cr_trapped', 348.0, -2.3, 'z=1.5,dx=320'),  # Annabelle's face (cut 350.4); at L it crossed x 840
  ]))

# ---- s08 #3 The Devil Made Me Do It (30%): Arne's real line ----
X.append(sec('s08', [
  (0, 'dm_promise', 19.85, -3.2, AR),  # 19.6 is still the wide Ed/Lorraine shot; Isla 19.83-23.15
  ('this one is the smartest', 'dm_calvary', 64.0, -6.0, AR),  # Isla in the dark (verify a clean span in 64-92)
  ('because the demon never', 'co_stab', 58.5, -3.0),      # Isla's altar: the candle fire flaring among the curse totems
  ('a witch puts a curse', 'dm_calvary', 40.78, -0.68, AR),
  ('on you', 'dm_calvary', 41.52, -0.7, o(AR, 'g=1.25')),  # hands placing the totem 40.78-41.47, then a cut to Arne's arm (blue)
  ('and the demon makes you', 'dm_david', 301.12, -1.95, 'g=1.25'),  # Arne snarling, possessed, close (301.1-303.1); 44.5 was a totem insert cutting at 44.9 to Arne's arm, no fire
  ('arne johnson stabs', 'dm_bruno_b', 144.55, -1.2),  # Bruno dancing drunk 144.55-145.77 (144.0 is Debbie/Arne, cut at 145.8)
  ('his landlord', 'dm_bruno_b', 156.3, -0.5),  # knife slides across the floor 156.27-156.85 (156.2 is Arne's back)
  ('twenty-two times', 'dm_bruno_b', 174.31, -0.35, 'a=-16,g=1.25'),
  ('times', 'dm_bruno_b', 174.75, -0.45, 'a=-16'),  # Arne's hand grabs the knife off the floor, blade up (174.73-175.2); 174.4-175.9 held 4 cuts (scream / grab / dark doorway / scream)
  ('a girl named jessica', 'dm_vision', 102.6, -1.4, o(AR, 'g=1.25')),  # Jessica smiling 102.55-104.05; cuts at 104.07 (Katie), 105 (hands), 107-109 (back and forth)
  ('stabs her best friend', 'dm_vision', 154.1, -2.5, o(AR, 'g=1.25')),  # 154.0 is the last knife frame; Katie's frightened face 154.07-156.65
  ('twenty-two times#2', 'dm_vision', 185.47, -0.6, AR),
  ('times#2', 'dm_vision', 186.2, -1.25, AR),  # Jessica's bloodied hand lets the knife drop (185.45-186.13); 185.0 is Ed/Drew daylight. Mild blood on the forearm only
  ('and then dies too', 'co_stab', 36.8, -3.2),  # 36.5 is Ed's face; the sheet-covered body 36.78-40.15. No Ed in this shot: comment -> "the sheet-covered body on the morgue table"
  ('the witch kills her own father', 'dm_altar', 52.42, -2.3, AR),  # 52.0 is a wide lamp shot; close: a ringed hand grips Kastner's head 52.4-54.75, then a wide at the desk
  ('and turns ed against', 'dm_final', 102.65, -1.1),  # Ed possessed, bleeding eyes 102.6-103.75 (rises out of black), cut to Lorraine at 103.77
  ('until he nearly kills her', 'dm_final', 104.0, -4.0),  # Lorraine pinned on the floor looking up at him (never 72-89 or 121-130)
  ("you can't run from a curse", 'dm_david', 330.0, -1.3, 'z=1.35,flip=1'),  # extreme eyes close-up spans x 250-1300: under L the left eye is cropped and the right one sits under the card; flipped, the red-ringed eye lands at x~500. Black at 331.4
  ('because the one attacking', 'co_stab', 67.75, -1.6, L),  # 66.0-67.7 is a curse-totem insert; Arne hunched in his cell 67.72-69.4 (head at x~540 under L), then totem again
  ('and only smashing', 'dm_final', 148.5, -2.0, 'z=1.1,dx=90'),  # Ed swings the hammer (wide) to 150.5, cut to Lorraine at 150.53. Ed at x~340-610 under L
  ('can break it', 'dm_final', 153.3, -2.75, 'z=1.1,dx=90,flip=1'),  # 152.4 is still the dust close-up; the wide of the altar table cracking and collapsing 152.72-156.1 (break point x~700 under L)
  ('survival rate', 'dm_promise', 49.5, -4.0, ARL),        # Isla's pale face slowly lit in the dark
  ], inserts=[
    ins('makes you the killer', 1.1, 'film', shots=[(0, 'dm_david', 319.77, 1.0, 'lufs=-17')], sub='Take me!'),
  ]))   # Phase B: check Arne is on screen while he speaks

# ---- s09 #2 The Nun II (12%) ----
X.append(sec('s09', [
  (0, 'n2_maurice', 160.5, -8.9),  # 160.0-160.35 is Irene's face; Valak silhouette 160.4-169.4
  ('this is valak again', 'n2_exorcise', 2.0, -1.1),  # snarl close-up 1.95-3.15, then a wide
  ('and this valak is far', 'n2_lucy', 21.82, -1.15),
  ('stronger than any demon', 'n2_lucy', 3.45, -2.0),  # 83.5 was a wide; the roar 84.3-85.45 is the SAME take as n2_exorcise 2.0-3.1 on the line before (dupe). New: Valak grinning, glowing eyes, red teeth 21.8-22.97 (842p)
  ("it's hunting for the eyes", 'co_neck_b', 187.7, -0.85),  # reliquary in flames 187.95-188.57, cut to a dark wide
  ('of saint lucy', 'co_neck', 136.15, -3.55),  # 140-144.1 is near-black; the vision: a veiled figure silhouetted against a wall of fire 136.12-139.75 (fades to black)
  ('a holy relic', 'co_neck_b', 191.9, -0.5, 'g=1.25'),  # 191.0 is the nun's face; close of hands holding the relic 191.88-192.45 (a wider hands shot 191.05-191.85 is the alternative)
  ('that would give it back', 'n2_exorcise', 49.0, -1.35),
  ('the power it had', 'n2_lucy', 9.5, -1.25),  # 47.5 is a painted portrait, 47.75-48.95 Irene's face; the illuminated manuscript page 48.98-50.35
  ('and it has been hiding', 'n2_maurice', 38.5, -4.8, 'g=1.4'),  # Maurice possessed to 43.35, cut to Sophie
  ('the man who saved irene', 'n2_maurice', 118.5, -6.0, 'g=1.4'),  # Maurice grinning, possessed
  ('it lifts a priest', 'n2_burn', 370.45, -0.8, 'g=1.4'),
  ('into the air', 'n2_burn', 371.32, -0.53, 'g=1.4'),  # wide (priest tiny) cuts at 371.28 to the close: Noiret in mid-air, arms spread, 371.3-371.88; wide burning from 371.9
  ('and burns him alive', 'n2_burn', 377.0, -1.0, 'a=-18,g=1.25'),  # the altar boy Jacques screaming (cut on the boy, not the burning face)
  ('snaps a young', 'n2_deliv', 131.1, -1.3),              # Valak in red light, her pale face in the doorway
  ("girl's neck", 'n2_deliv', 132.72, -0.9),  # Valak doorway shot runs to 132.67; the delivery girl (cap, checked shirt) scrambling on the corridor floor 132.7-133.65
  ('kills the headmistress', 'n2_altar', 89.0, -0.95, 'g=1.4'),
  ('of a', 'n2_altar', 90.03, -0.45),  # her terrified face 89.0-89.97, cut to a closer angle 90.0-90.45, then the chapel wide
  ('school', 'n2_altar', 94.92, -0.65),  # 94.0-96.6 holds 6 cuts. Madame Laurent screaming as the altar boy attacks 94.9-95.58 (boy alone 94.42-94.78 is the alt, 0.35 s). Still well before 98
  ('and leaves a trail', 'n2_burn', 383.0, -11.5),         # the possessed Maurice walking off into the foggy Tarascon street (title card from 396)
  ('sister irene only survives', 'n2_lucy', 24.0, -1.75),  # Irene in mid-air above the fire to 25.75; white flash 25.8, cut 26.1
  ('being set on fire', 'n2_lucy', 41.1, -1.45),  # crucified pose in mid-air, flames at her feet 41.07-42.6; cut to her flame-lit face 42.63 (that face shot 42.65-47.3 is the alt)
  ('because she comes from', 'n2_exorcise', 63.05, -1.15),  # 62.0 is Irene (dark), 62.1-62.95 a young woman in a headscarf; Irene's mother (same woman as 75.9) 63.0-64.25
  ("saint lucy's own family", 'n2_exorcise', 75.9, -1.65),  # 75.0-75.85 is little Irene alone; the mother holding her 75.87-77.58
  ('and it takes a miracle', 'n2_exorcise', 87.85, -4.9),  # 86.0-87.7 is Irene's face, the barrels, a red blur; the blood mist around Valak (wide) 87.8-92.9
  ("you're not from saint", 'n2_exorcise', 98.0, -3.0, o(L, 'flip=1')),  # Valak's head is at x~1150-1250 (x~950 under L, under the card); flipped + L puts it at x~300-435. Span 98.0-101.08 confirmed one shot
  ('survival rate', 'n2_exorcise', 23.15, -1.68, L),  # 21.0-21.75 is Irene's face (21.8 grin now on "and this valak is far"); Valak close-up, glowing eyes, 18.97-20.97, face at x~540 under L
  ]))

# ---- s10 #1 The Nun (5%) ----
X.append(sec('s10', [
  (0, 'co_valak0', 4.0, -7.5),                             # Valak rising out of the water
  ('this is valak at full power', 'spooky_nun', 1092.45, -0.6),
  ('at full power', 'spooky_nun', 1049.3, -5.0),  # 1092.0-1092.4 is a nun lunging (wide); Valak roaring close-up 1092.43-1093.05
  ('guarding its own doorway', 'spooky_nun', 1117.8, -2.5, 'g=1.4'),  # 1116.5-1117.7 is the dark corridor; "Finit hic Deo" door 1117.75-1120.35, cut to Irene
  ('in an abbey in romania', 'n1_open', 0.0, -8.7, o(AR, 'g=1.4')),  # a figure steps in at 8.8
  ('before irene even arrives', 'n1_open', 38.0, -1.4, AR),  # Oana screaming to 39.45; 39.5-40 is the floor and her bloody hand (owner rule)
  ('it has killed every nun', 'spooky_nun', 999.0, -7.0, 'g=1.4'),  # 998.0-998.85 is Frenchie by a bloodied body; overhead dead nuns from 998.9 to past 1006.4
  ('and the sisters she prays with', 'n1_pray', 21.0, -7.3),  # 8-21 holds ~9 cuts; Irene praying among the nuns, candles, one push-in 20.9-28.6
  ('turn out to have been dead', 'n1_pray', 39.0, -20.0, 'g=1.4'),  # one overhead move 37-59.9; the empty habits read clearly from ~39; cut at 60.0
  ('it buries father burke', 'co_buried_b', 75.6, -2.4),  # 76-88 holds ~7 cuts; one shot of Burke in the coffin flicking his lighter 74.9-78.03 (face lit from 76.6)
  *pick('s10', 'and drowns irene', [
    ('and drowns irene', 'co_valak0', 26.1, -1.6, 'g=1.4'),  # v1.1: 22.0-22.75 is Valak standing in the water, 22.85-25.0 Irene waist-deep, 25-26 a wide; Irene thrown back thrashing in the flooded crypt 26.05-27.72
  ], [
    ('takes over irene', 'n1_poss', TODO, TODO),             # v1 GAP: Irene possessed (n1_poss age-gated) or the film file
    ('and drowns her', 'co_valak0', 26.1, -1.6),  # v1 branch, same reason
  ]),
  ('the church sent', 'co_valak0', 64.0, -1.0, 'g=1.4'),
  ('a priest', 'spooky_nun', 317.2, -0.65, 'g=1.4'),
  ('a nun', 'spooky_nun', 1080.42, -1.15, 'g=1.4'),  # relic vial in Irene's hand to 65.05, cut to Valak
  ('and the actual blood', 'co_valak0', 84.65, -1.6, 'g=1.25'),  # 83.6-84.55 Valak + Irene's arm; the glass vial of Christ's blood swinging on its chain 84.6-86.9
  ('and even then', 'co_valak0', 96.5, -1.45, 'g=1.4'),  # Valak's face soaked in the spat blood 96.47-97.97, cut to the water surface (red cloud) at 98.0
  ('hiding inside frenchie', 'co_valak0', 168.35, -2.05),  # 160-176 holds ~8 cuts (floor, CPR, Irene, Frenchie...); Frenchie bent over the drowned Irene, frantic, 168.3-170.45
                                                           # on his neck is in n1_fight, age-gated: prefer it when the owner runs the commands)
  ("if the vatican's best", 'co_valak0', 118.0, -3.2, o(L, 'flip=1')),  # clawing shot to 121.3, then Irene underwater 121.4-123.5, Valak again 123.6. Face at x~1100 = x~813 under L; flipped + L -> x~435
  ('survival rate', 'co_valak0', 87.2, -3.2, L),           # Valak close-up, steady, holding the relic vial
  ]))

# ---- s11 outro: the hide-and-clap scene plays out under the last lines, the two claps end the video ----
X.append(sec('s11', [
  (0, 'still_posterwall', 1.0, -4.0),                      # all 9 posters (callback to the cold open)
  ('from the doll', 'universe', 880.0, -3.2, C1),  # doll close-up to 883.25, cut to the nurse
  ('to the valak', 'spooky_nun', 1063.0, -2.1),  # 1062.0-1062.95 is a man's face; Valak close-up 1063.0-1065.15, then hands/blur
  ('which one would you least', 'universe', 22.5, -8.5, C1),  # burned "The Conjuring (2013)" caption bottom-left until 22.3
  ('tell me in the comments', 'universe', 136.4, -5.6, C1),  # 136.0-136.35 is black before the match strikes; cut ~142.1
  ('i went through every death', 'universe', 151.0, -2.7, C1),  # 145.6-146.55 over-shoulder, 146.6-147.35 front, 147.4-150.85 BLACK (match out). Front: she strikes a new match, face lit, 150.95-153.75
  ("and we're a small channel", 'universe', 153.82, -3.1, C1),  # over her shoulder: the lit match held out into the dark 153.78-156.95
  ('thanks for watching', 'universe', 157.0, -2.6, C1),    # Carolyn holding the match, waiting
  ], inserts=[
    ins('END', 0.72, 'clap', shots=[(0, 'universe', 159.6, 1.0, o(C1, 'lufs=-22'))]),  # two claps 159.94/160.14, the match dies ~160.25, black at 160.32 (real audio, no subtitle)
  ], extra=[('png', '../ep04/tiles/subscribe.png', 'every subscribe', 'thanks for watching')]))
