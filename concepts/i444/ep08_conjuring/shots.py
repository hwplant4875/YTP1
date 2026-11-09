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
  (0, 'c2_painting', 136.5, -2.3),                         # FRAME 0: Valak's face, big and bright (the painting scene, The Conjuring 2)
  ('will burn you alive', 'co_burn_4k', 157.8, -1.1, 'a=-18'),  # The Nun II: full-frame fire on the burning priest (no flesh visible)
  ('in midair', 'co_burn_4k', 154.9, -1.5),                # wide church: the priest burning in the air above the altar
  ('bury you alive', 'co_buried_b', 100.0, -5.9),          # The Nun: Father Burke lying in the coffin, lighter lit
  ('snap your neck', 'n2_deliv', 137.8, -0.6, 'a=-16'),    # The Nun II: the delivery girl screams as Valak lifts her (cut before her feet at 138.5)
  ('make you stab', 'dm_vision', 153.0, -0.9, AR),         # DMMDI: the knife in Jessica's hand
  ('your best friend', 'dm_vision', 160.0, -0.9, AR),      # Katie crying in terror (cut before any wound)
  ('twenty-two times', 'dm_vision', 156.7, -1.9, AR),      # possessed Jessica, white eyes
  ('or turn your own mother', 'co_mother_c', 305.9, -5.1), # The Conjuring: possessed Carolyn's grinning face next to Roger
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
  (0, 'ach_room', 10.0, -8.0, L),                          # the Warrens' room of cursed objects, wide and dark (verify a clean 8 s in 0-38)
  ('comes for you', 'n2_deliv', 126.2, -3.2, L),           # Valak in the nun habit at the end of a hallway that turns red
  ('and every one is different', 'c2_grave', 118.0, -6.0, L),   # The Conjuring 2: Janet speaking in Bill Wilkins's voice
  ("one can't touch you", 'ach_devil_cz', 300.0, TODO, L), # the girls shut Annabelle back in the case (verify a clean 2.5 s in 298.2-305)
  ('one needs you to hand', 'a14_baby', 58.7, -1.7, L),    # "her SOUL" written on the nursery ceiling (s03 uses it too: look for a 2nd angle of the writing after 60.4)
  ('and one has wiped out', 'co_valak0', 93.0, -1.3, L),   # The Nun: Valak's face, mouth open
  ('so we score', 'lr_end', 46.0, -3.0, L),                # Last Rites: Ed and Lorraine run in
  ('strength', 'co_mother_c', 240.0, -3.4, L),             # The Conjuring: Carolyn levitating in the chair under the sheet
  ('intelligence', 'dm_altar', 118.0, -5.0, ARL),          # DMMDI: the witch's altar room, a woman at the altar (verify)
  ('kill count', 'cr_wheel', 568.8, -4.4, L),              # Creation: Samuel's body on the floor (no close dead face)
  ('and possession', 'lr_end', 108.9, -1.1, L),            # Last Rites: possessed Judy's bloody grin, blue light
  ('which is how completely', 'c2_janet', 232.0, -6.0, L), # The Conjuring 2: possessed Janet's face behind the wall boards
  ('put it all together', 'spooky_nun', 1112.0, -3.0, L),  # The Nun: Irene with a candle in the crypt
  ]))
X[-1]['vfade'] = {'in': 0.2}

# ---- s02 #9 Annabelle Comes Home (95%) ----
X.append(sec('s02', [
  (0, 'ach_room', 38.0, -14.0),                            # Daniela standing among the artifacts (dark, wide)
  ('this annabelle', 'ach_devil_cz', 316.4, -1.5),         # Annabelle's face behind the glass over Daniela's shoulder
  ("because it's locked", 'ach_end', 57.7, -0.7),          # Annabelle in the glass case, close (0.7 s, slowed)
  ('a blessed glass case', 'ach_devil_cz', 285.0, -3.3),   # Judy's hand on the case glass, the doll's dress and red rose beside it
  ("in the warrens' room", 'ach_room', 244.0, -4.0),       # "DANGER! DO NOT TOUCH ANYTHING!" sign, pull back to the WARRENS DEMONOLOGY WITCHCRAFT door
  ('and as long as', 'ach_end', 92.9, -1.5),               # Daniela in the artifact room, Annabelle in the case behind her
  *pick('s02', 'lets the doll out', [
    ('when a teenager sneaks in', 'ach_room', 54.0, -4.0),   # v1.1: Daniela alone among the artifacts, her face (verify 54-58)
    ('and lets the doll out', 'ach_hands', 32.0, -5.0),      # Annabelle out of her case, under the sheet in Judy's bed (dark)
  ], [('when a teenager opens', 'GAP', TODO, TODO)]),       # v1 GAP: Daniela opening the case (in no clip): the film file
  ('it wakes up everything', 'ach_room', 236.6, -0.9),     # a burned-face spirit lunges in the artifact room
  ('in that room', 'ach_tv', 26.0, -18.0),                 # the haunted TV showing Daniela
  ('the ferryman', 'ach_ferry_b', 70.5, -2.5),             # the Ferryman's coin-eyed face lit by the lantern (dark)
  ('the babysitter', 'ach_ferry_b', 64.0, -3.8),           # Mary Ellen with the lantern, searching
  ('the bride takes over', 'ach_devil_cz', 148.2, -1.1),   # Daniela in the bride's veil and dress, standing over Judy in the dark
  ('her friend', 'ach_devil_cz', 150.7, -1.1),             # close: the veiled, possessed Daniela, blank dark-eyed stare
  ('a hellhound attacks', 'ach_wolf', 49.3, -1.0),         # the hellhound's claws through the car window (very dark)
  ('a boy outside', 'ach_wolf', 45.6, -1.2),               # Bob screaming in the car
  ('and a board game', 'ach_devil_cz', 195.6, -1.7),       # Judy sprawled on the rug next to the Feeley Meeley box (name legible)
  ('with dead hands', 'ach_devil_cz', 199.7, -4.5),        # overhead: grey dead hands reach out of the board and grab Judy's arm
  ('but in the whole movie', 'ach_end', 88.0, -1.8),       # the three girls together, Judy holding the crucifix
  ("and it's beaten by", 'ach_end', 82.4, -2.2),           # Mary Ellen, Daniela and Judy side by side
  ('who simply put the doll', 'ach_end', 74.0, -0.9),      # the girls pushing the doll into the case
  ('and lock it', 'ach_end', 80.3, -0.9),                  # the key turning in the case lock
  ('leave the glass shut', 'ach_end', 61.9, -2.6, L),      # Judy at the glass, Annabelle sitting inside the case
  ('survival rate', 'ach_end', 46.0, TODO, L),             # GAP: a long, clear doll close-up in the case (film file); else the girls' crucifix fight 46-81 (verify)
  ]))

# ---- s03 #8 Annabelle (2014) (80%) ----
X.append(sec('s03', [
  (0, 'a14_baby', 45.8, -2.2),                             # the Annabelle doll in Leah's crib, top shot
  ('this demon is more', 'a14_fire', TODO, TODO, AR),      # Mia sewing at home, calm (pick a clean 2-3 s in a14_fire 0-86)
  ("because it isn't locked", 'a14_basement', 73.0, -1.3), # the doll close-up on the nursery floor
  ('it lives in the doll', 'a14_baby', TODO, TODO),        # Mia in the nursery with the doll on the shelf (pick a clean 2 s in a14_baby 0-45 or 61-159)
  ('but it has one big weakness', 'a14_basement', 121.0, -1.6),  # the Annabelle demon/ghost standing at the bright window (the card has the rest)
  ('it needs a soul', 'a14_baby', 58.7, -1.7),             # "her SOUL" written on the ceiling (in-film writing)
  ('so it plays with you', 'a14_basement', 61.0, -2.4),    # Mia knocked flat on the floor, eye level
  ('starting a fire', 'a14_fire', 86.6, -1.4, AR),         # the popcorn pan bursts into flame on the stove
  ('in the kitchen', 'a14_fire', 108.5, -3.5, AR),         # the whole stove on fire, Mia behind
  ('chasing you through', 'a14_stairs', 48.5, -2.5),       # Mia running down the basement-storage stairwell (the horned demon flash at
                                                           # 65.0-65.3 can be cut in where a slot allows it)
  *pick('s03', 'then it steals', [], [
    ('and attacking the priest', 'a14_priest', TODO, TODO),  # v1 GAP: age-gated a14_priest (qa/age_gated.txt) or the film file
    ('then it takes over', 'a14_priest', TODO, TODO),        # v1 GAP: the demon in the priest's body (same source)
  ]),
  ("steals mia's baby", 'a14_baby', 55.3, -3.1),                  # Mia pulls the bundle from the crib: it is the doll, not Leah
  ('to force a trade', 'a14_basement', 64.0, -0.9),        # baby Leah on the bed (extend if 64.9-72 stays on Leah)
  ('in the end', 'a14_baby', 159.2, -2.4),                 # Evelyn (red headscarf) on the stairs (never her fall)
  ('who gives up her own life', 'a14_basement', 126.0, -2.0),  # Mia clutching Leah, saved (Evelyn's act is never shown)
  ('never offer it your soul', 'a14_basement', 122.6, -2.8, L),  # the Annabelle demon at the window, close (122.6-125.4), through the % line
  ]))

# ---- s04 #7 The Conjuring (65%) ----
X.append(sec('s04', [
  (0, 'c1_sheets', 20.0, -6.5),                            # the Perron farmhouse, sheets blowing on the line
  ('this demon is far', 'c1_sheets', 28.0, -1.5),          # Lorraine stares at the house
  ("because it doesn't need", 'c1_sleep', 20.0, -6.0),     # Christine staring at the dark corner behind her door ("someone behind the door", verify)
  ('bathsheba was a witch', 'co_mother_b', 257.5, -1.5),   # Bathsheba's grey face lunging at Lorraine in the cellar
  ('who gave her own baby', 'co_mother_b', 263.5, -2.0),   # Bathsheba's face close-up on the wardrobe (her backstory is told over her face;
                                                           # the sacrifice itself is only in c1_land under burned subtitles: the film file)
  ('and she curses anyone', 'c1_dog_b', 12.0, -5.5),       # the Perrons unloading the truck at the farmhouse (recap clip: its corner bug is cropped by CLIPOPT)
  ('she stops every clock', 'c1_land', 141.0, -4.5),       # the alarm clock stopped at about 3:07 (no subtitle after 140.8)
  ('leaves bruises', 'c1_dog_b', 56.0, -1.6),              # the bruise on Carolyn's leg as she gets up
  ('pulls at the girls', 'c1_sleep', 1.0, -3.0),           # Christine asleep, jerks awake (the tug itself: c1_foot age-gated / film)
  ('and kills the family dog', 'c1_dog_b', 87.0, -3.0),    # Roger finds Sadie lying in the weeds (small, wide; weak: film file)
  ('then she takes over', 'co_mother_c', 291.5, -1.5),     # possessed Carolyn laughing
  ('completely', 'universe', 476.5, -3.5, C1),             # possessed Carolyn held down by the men, screaming
  ('because in every family', 'universe', 444.5, -2.5, C1),  # possessed Carolyn struggles with the scissors over her daughter (dark, fast)
  ('she makes the mother', 'c1_feed', 96.0, -4.0),         # Carolyn and the scissors on the floor
  ('the perrons only survive', 'co_mother_c', 10.0, -5.0), # Ed reads the rite from the book in the cellar
  ('and lorraine reaches', 'universe', 690.5, -1.3, C1),   # the sunny beach memory, the mother
  ('with a happy memory', 'universe', 695.5, -2.0, C1),    # the girls running on the beach
  ('she only wants the mother', 'universe', 702.0, -14.0, o(C1, L)),  # Ed's hand on possessed Carolyn's head, she screams (through the % line)
  ]))

# ---- s05 #6 The Conjuring 2 (55%): two real film lines from Lorraine ----
X.append(sec('s05', [
  (0, 'universe', 1086.0, -5.0, C2),                       # Janet on the sofa, then the Enfield street in the rain
  ('this is the first time', 'c2_painting', 204.0, -2.5),  # Valak steps out of the painting
  ("and it's much smarter", 'c2_painting', 58.0, -5.0),    # Valak standing in the dark behind Lorraine
  ('it hides behind', 'c2_vision', 0.0, -11.0),            # Bill Wilkins in his armchair, Lorraine across the room (800p)
  ('so everyone thinks', 'c2_vision', 55.8, -1.0),         # Valak's face appears behind Bill (never 57.5-59)
  ("it blocks lorraine's visions", 'c2_vision', 12.0, -3.0),  # Lorraine staring, unsettled
  *pick('s05', 'fight his way in', [], [("shows her ed's death", 'GAP', TODO, TODO)]),   # v1 GAP: Lorraine's vision of Ed impaled: the film file
  ('and sends the crooked man', 'c2_crooked', 65.8, -1.4), # the Crooked Man's shape in the tent
  ('after the youngest boy', 'c2_crooked', 73.5, -2.0),    # the Crooked Man lunges at Billy
  ('then it takes over janet', 'c2_janet', 219.5, -1.5),   # possessed Janet grinning in the wall
  *pick('s05', 'fight his way in', [
    ('and ed has to fight', 'c2_janet', 214.0, -4.5),        # v1.1: Ed forcing his way through to Janet (verify it reads as fighting his way in)
  ], [
    ('walks her to a window', 'GAP', TODO, TODO),            # v1 GAP: Janet at the window (never a jump): the film file
    ('and ed nearly dies', 'GAP', TODO, TODO),               # v1 GAP: Ed hanging from the curtain: the film file
  ]),
  ('but valak has one', 'c2_name_b', TODO, TODO, AR),      # Lorraine in the rain with the bible (pick a clean 2-3 s in c2_name_b 0-58)
  ('if you know its name', 'c2_name_b', 58.0, -4.0, AR),   # Lorraine's hand writing the name in the bible
  ('and lorraine sends it back', 'c2_name', 44.0, -3.0, AR),  # Lorraine shouts the name at Valak
  ('learn the name', 'c2_name', 55.5, -1.5, ARL),          # Valak's face before it is pulled back
  ('survival rate', 'c2_painting', 137.2, -1.6, L),        # Valak's face (the painting scene; s00 opens on 136.5-137.1)
  ], inserts=[
    ins('you have power over it', 2.05, 'film', shots=[(0, 'c2_name', 39.85, 1.0, o(AR, 'lufs=-17'))], sub='You are Valak.'),
    ins('just by saying it', 2.0, 'film', shots=[(0, 'c2_name', 52.73, 1.0, o(AR, 'lufs=-17'))], sub='I condemn you back to hell.'),
  ]))   # Phase B: check Lorraine is on screen while she speaks in both inserts (else start on the Valak reaction and keep the audio)

# ---- s06 #5 The Conjuring: Last Rites (45%) ----
X.append(sec('s06', [
  (0, 'lr_family', 102.0, -5.0),                           # the Smurl street at night, car headlights, the Smurl duplex
  ('this demon is stronger', 'lr_end', 42.0, -3.0),        # the ornate mirror on the wall, glowing
  ('than that valak', 'lr_exorcism', 514.8, -0.6),         # the mirror demon's face, blue-lit, fanged (a flash)
  ('and it came closer', 'lr_exorcism', 56.0, -0.8),       # Lorraine bloodied in the attic
  ('to killing the warrens', 'lr_judy', 230.0, -6.0),      # Judy choked in the mirror room (verify)
  ('it lives inside', 'lr_preview', 184.0, -6.0),          # the mirror hanging in the Smurl dining room
  ('and in nineteen sixty-four', 'lr_birth', 20.0, -10.0), # 1964: Lorraine in labour, crying (no mirror in this clip)
  ('it nearly killed judy', 'lr_birth', 55.0, -6.5),       # hands over the still, wrapped baby
  ('twenty-two years later', 'lr_judy', 50.0, -6.5),       # adult Judy in the wedding dress in the mirror room
  ('it uses three ghosts', 'lr_axe', 234.8, -0.5),         # a grey ghost face snarling (spirit 1, a flash)
  ('three ghosts', 'lr_exorcism', 64.0, -2.5),             # the axe man with the lantern (spirit 2)
  ('to haunt the smurl family', 'lr_exorcism', 38.0, -4.5),  # the old woman ghost in the attic (spirit 3, dark)
  ('drives the priest', 'lr_priest', 30.0, -7.5),          # Father Gordon alone in his office
  ('to his death', 'lr_priest', 138.0, -2.0),              # his eyes, close (CUT before 140.5: never the hallway or the fall)
  ('gives ed a heart attack', 'lr_exorcism', 346.2, -1.3), # Ed on the floor grimacing in pain, Lorraine over him
  ('and takes over judy', 'lr_end', 177.0, -3.0),          # possessed Judy snarling (blood in the mouth, not extreme)
  ("ed's exorcism", 'lr_end', 24.0, -1.5),                 # Ed raises his hand with the bible at the mirror
  ('even work', 'lr_end', 82.0, -1.4),                     # Ed, then the bible burning
  ('and only the whole family', 'lr_exorcism', 503.7, -2.5),  # hands on the glass, it cracks
  ('can break the mirror', 'lr_exorcism', 513.7, -0.9),    # Lorraine and Judy press their hands on it, the demon screaming in the reflection
  ('if it wants you', 'lr_exorcism', 480.0, -4.0, L),      # Lorraine holding Judy
  ('survival rate', 'lr_axe', 539.8, -1.2, L),             # the old-woman ghost grinning (clean)
  ]))   # lr_end t = lr_exorcism t - 330 (same footage): never use both for one moment

# ---- s07 #4 Annabelle: Creation (40%) ----
X.append(sec('s07', [
  (0, 'cr_sam', 29.3, -7.7),                               # the Annabelle doll in a chair, bright, dead centre
  ('this is where the annabelle', 'cr_wasnt', 0.0, -2.6),  # the doll at a tea table with the girl in Bee's dress
  ('and unlike the last one', 'cr_trapped', 352.0, -5.0),  # possessed Janice attacking Linda (verify)
  ('it pretends to be bee', 'cr_wasnt', 15.0, -4.5),       # the demon as Bee, walking in Bee's room
  ('so her heartbroken parents', 'cr_wasnt', 38.0, -4.0),  # Esther (half-masked) telling the story (AVOID 34-36, her clawed eye)
  ('let it into the doll', 'cr_wasnt', 60.8, -2.2),        # the doll's face close, sinister
  ('then it goes after', 'cr_sam', 37.8, -5.2),            # Sister Charlotte and the orphans unloading the truck
  *pick('s07', 'drags janice', [
    ('it drags janice', 'cr_wheel', 79.4, -1.8),             # v1.1: unseen hands grip Janice's shoulders from behind her wheelchair
    ('out of her wheelchair', 'cr_wheel', 86.6, -1.0),       # low shot: dark skirt and boots running, pushing the chair across the dirt
    ('into a barn', 'cr_wheel', 94.7, -2.3),                 # Janice thrown from the chair, face down on the barn floor
  ], [
    ('it throws janice', 'cr_soul', 155.0, -2.3),            # v1: Janice riding the stairlift
    ('off her stairlift', 'GAP', TODO, TODO),                # v1 GAP: the throw (cr_soul ends before it): the film file
  ]),
  ('and takes over her body', 'cr_stair', 125.6, -2.0),    # the demon forces itself into Janice's mouth in the barn (end card from ~128)
  ('through her', 'cr_sam', 16.0, -8.0),                   # Samuel holding up the crucifix, his fingers bending back (cut before 26)
  ('and kills him', 'cr_sam', 59.8, -1.2),                 # his body on the floor, wide (never 63-64)
  *pick('s07', 'drags janice', [], [('it kills his wife', 'cr_dumb', TODO, TODO)]),   # v1 GAP: Esther's death (cr_dumb age-gated) or the film file
  ('and twelve years later', 'cr_end', 8.8, -6.2),         # the Higgins family photos (after the burned "12 YEARS LATER" ends ~8.5)
  ('it kills the couple', 'cr_end', 19.0, -3.5),           # the Higgins couple woken in bed
  ('who adopted her', 'cr_end', 39.4, -2.1),               # grown Annabelle Higgins grabs her father's throat (cut on the grab)
  ('five girls and a nun', 'cr_well', 116.4, -3.2),        # Sister Charlotte holding Linda in the field
  ('but only because they run', 'cr_well', 121.0, -6.8),   # the girls running across the field at night
  *pick('s07', 'stays inside janice', [
    ('and the demon stays', 'cr_trapped', 256.3, -5.5),      # v1.1: possessed Janice in a blue nightgown, a sly demonic smile, holding a doll
  ], [('and the demon walks away', 'GAP', TODO, TODO)]),    # v1 GAP: Janice leaving the orphanage: the film file
  ("if you're the weakest", 'cr_soul', 140.5, -8.0, L),    # Janice, scared, on the dark landing
  ('survival rate', 'cr_trapped', 348.0, -2.3, L),         # Annabelle's face close-up in the dark, alone, still
  ]))

# ---- s08 #3 The Devil Made Me Do It (30%): Arne's real line ----
X.append(sec('s08', [
  (0, 'dm_promise', 19.6, -3.0, AR),                       # the Occultist (Isla), gaunt, dark coat, raising her hand in the tunnel
  ('this one is the smartest', 'dm_calvary', 64.0, -6.0, AR),  # Isla in the dark (verify a clean span in 64-92)
  ('because the demon never', 'co_stab', 58.5, -3.0),      # Isla's altar: the candle fire flaring among the curse totems
  ('a witch puts a curse', 'dm_calvary', 41.0, -1.4, AR),  # hands placing the totem on the candle altar
  ('and the demon makes you', 'dm_calvary', 44.5, -2.0, AR),  # the fire flaring on the altar
  ('arne johnson stabs', 'dm_bruno_b', 144.0, -2.4),       # Bruno, the landlord, dancing drunk in the room
  ('his landlord', 'dm_bruno_b', 156.2, -0.6),             # a folding knife slides across the wooden floor
  ('twenty-two times', 'dm_bruno_b', 174.4, -1.5, 'a=-16'),  # Arne screams out of the dark, grabs the knife, lunges (ends before the black at 176.6)
  ('a girl named jessica', 'dm_vision', 102.5, -7.5, AR),  # Jessica smiling (Lorraine's vision)
  ('stabs her best friend', 'dm_vision', 154.0, -2.5, AR), # Katie's frightened face
  ('twenty-two times#2', 'dm_vision', 185.0, TODO, AR),    # the knife again (verify a clean span at 185; s00 uses 153.0-153.9 and 156.7-158.6)
  ('and then dies too', 'co_stab', 36.5, -3.0),            # the sheet-covered body on the morgue table, Ed beside it (Jessica's fall is never shown)
  ('the witch kills her own father', 'dm_altar', 52.0, -5.5, AR),  # Father Kastner at his desk, a ringed hand grips his head from behind
  ('and turns ed against', 'dm_final', 102.6, -1.4),       # Ed possessed, bleeding eyes
  ('until he nearly kills her', 'dm_final', 104.0, -4.0),  # Lorraine pinned on the floor looking up at him (never 72-89 or 121-130)
  ("you can't run from a curse", 'dm_david', 330.0, -1.4, L),  # Arne's black-ringed, possessed eyes
  ('because the one attacking', 'co_stab', 66.0, -4.0, L), # Arne alone, hunched in his cell
  ('and only smashing', 'dm_final', 148.0, -3.5, L),       # Ed swings the hammer at the altar
  ('can break it', 'dm_final', 152.4, -3.4, L),            # the altar table cracks and collapses
  ('survival rate', 'dm_promise', 49.5, -4.0, ARL),        # Isla's pale face slowly lit in the dark
  ], inserts=[
    ins('makes you the killer', 2.15, 'film', shots=[(0, 'dm_david', 315.93, 1.0, 'lufs=-17')], sub='Leave him alone and take me!'),
  ]))   # Phase B: check Arne is on screen while he speaks

# ---- s09 #2 The Nun II (12%) ----
X.append(sec('s09', [
  (0, 'n2_maurice', 160.0, -9.0),                          # Valak's silhouette backlit in blinding light
  ('this is valak again', 'n2_exorcise', 2.0, -1.5),       # Valak snarls (1080p)
  ('and this valak is far', 'n2_lucy', 83.5, -2.0),        # Valak roaring, fangs (842p)
  ("it's hunting for the eyes", 'co_neck_b', 188.0, -0.6), # the golden reliquary in flames (Irene's vision)
  ('of saint lucy', 'co_neck', 140.0, -5.0),               # the vision of Saint Lucy and the nun in fire (verify in 134-163)
  ('a holy relic', 'co_neck_b', 191.0, -1.4),              # hands holding the relic
  ('that would give it back', 'n2_exorcise', 47.5, -2.0),  # an illuminated manuscript page of angels and demons
  ('and it has been hiding', 'n2_maurice', 38.5, -5.0),    # Maurice (Frenchie) possessed, black bleeding eyes
  ('the man who saved irene', 'n2_maurice', 118.5, -6.0),  # Maurice grinning, possessed
  ('it lifts a priest', 'n2_burn', 370.6, -1.4),           # Father Noiret floating in mid-air above the altar (s00 uses the burning, co_burn_4k)
  ('and burns him alive', 'n2_burn', 377.0, -1.0, 'a=-18'),  # the altar boy Jacques screaming (cut on the boy, not the burning face)
  ('snaps a young', 'n2_deliv', 131.1, -1.3),              # Valak in red light, her pale face in the doorway
  ("girl's neck", 'n2_deliv', 132.5, -1.4),                # the girl falls and scrambles backwards (s00 has the scream at 137.8)
  ('kills the headmistress', 'n2_altar', 89.0, -2.0),      # Madame Laurent's terrified face in the chapel
  ('school', 'n2_altar', 94.0, -2.6),                      # the demon altar boy lunges (cut BEFORE 98, her bloodied face)
  ('and leaves a trail', 'n2_burn', 383.0, -11.5),         # the possessed Maurice walking off into the foggy Tarascon street (title card from 396)
  ('sister irene only survives', 'n2_lucy', 24.0, -2.0),   # Irene lifted in mid-air, fire below
  ('being set on fire', 'n2_lucy', 41.5, -5.5),            # her face lit by the flames, screaming but not burning
  ('because she comes from', 'n2_exorcise', 62.0, -1.4),   # Irene's mother (flashback)
  ("saint lucy's own family", 'n2_exorcise', 75.5, -2.5),  # the mother holding little Irene
  ('and it takes a miracle', 'n2_exorcise', 86.0, -6.0),   # red blood mist bursting from the wine barrels around Valak
  ("you're not from saint", 'n2_exorcise', 98.0, -3.0, L), # Valak's face breaking apart
  ('survival rate', 'n2_lucy', 21.5, -1.5, L),             # Valak grinning, teeth
  ]))

# ---- s10 #1 The Nun (5%) ----
X.append(sec('s10', [
  (0, 'co_valak0', 4.0, -7.5),                             # Valak rising out of the water
  ('this is valak at full power', 'spooky_nun', 1092.0, -1.5),  # Valak roaring
  ('guarding its own doorway', 'spooky_nun', 1116.5, -3.0),  # the crypt door inscribed "Finit hic Deo" (God ends here)
  ('in an abbey in romania', 'n1_open', 0.0, -9.0, AR),    # the abbey corridor
  ('before irene even arrives', 'n1_open', 38.0, -2.0, AR),  # Sister Oana screaming before her death (never 40-54 or the rope from 68)
  ('it has killed every nun', 'spooky_nun', 998.0, -8.0),  # overhead: the dead nuns lying on the floor
  ('and the sisters she prays with', 'n1_pray', 8.0, -18.0),  # Irene praying among the nuns
  ('turn out to have been dead', 'n1_pray', 38.0, -20.0),  # the nuns gone, only empty habits on the floor
  ('it buries father burke', 'co_buried_b', 76.0, -12.0),  # Burke in the coffin lighting matches (s00 uses 100-105.9)
  *pick('s10', 'and drowns irene', [
    ('and drowns irene', 'co_valak0', 22.0, -4.0),           # v1.1: Irene thrashing in the flooded crypt
  ], [
    ('takes over irene', 'n1_poss', TODO, TODO),             # v1 GAP: Irene possessed (n1_poss age-gated) or the film file
    ('and drowns her', 'co_valak0', 22.0, -4.0),             # Irene thrashing in the flooded crypt
  ]),
  ('the church sent', 'co_valak0', 64.0, -2.5),            # the relic vial with the blood of Christ
  ('and the actual blood', 'co_valak0', 84.0, -2.0),       # Irene grabbing the vial near Valak
  ('and even then', 'co_valak0', 96.5, -2.5),              # the blood hits Valak (red cloud)
  ('hiding inside frenchie', 'co_valak0', 160.0, -16.0),   # Frenchie reviving the drowned Irene (the man Valak hides in; the inverted cross
                                                           # on his neck is in n1_fight, age-gated: prefer it when the owner runs the commands)
  ("if the vatican's best", 'co_valak0', 118.0, -8.0, L),  # Valak clawing its melting face
  ('survival rate', 'co_valak0', 87.2, -3.2, L),           # Valak close-up, steady, holding the relic vial
  ]))

# ---- s11 outro: the hide-and-clap scene plays out under the last lines, the two claps end the video ----
X.append(sec('s11', [
  (0, 'still_posterwall', 1.0, -4.0),                      # all 9 posters (callback to the cold open)
  ('from the doll', 'universe', 880.0, -3.5, C1),          # the Annabelle doll close-up (The Conjuring's prologue)
  ('to the valak', 'spooky_nun', 1062.0, -4.0),            # The Nun: Valak close-up
  ('which one would you least', 'universe', 22.0, -9.0, C1),  # Carolyn walking her dark hallway (after the burned title ends ~20)
  ('tell me in the comments', 'universe', 136.0, -6.0, C1),   # Carolyn in the cellar lighting a match
  ('i went through every death', 'universe', 146.0, -2.0, C1),  # the match lit in the dark (extend if 148-151 is the same shot)
  ("and we're a small channel", 'universe', 151.0, -2.0, C1),   # the match in the dark (extend if 153-157 is clean)
  ('thanks for watching', 'universe', 157.0, -2.6, C1),    # Carolyn holding the match, waiting
  ], inserts=[
    ins('END', 2.2, 'clap', shots=[(0, 'universe', 159.6, 1.0, o(C1, 'lufs=-22'))]),  # two hands clap beside her, the match dies (real audio, no subtitle); trim to the dark
  ], extra=[('png', '../ep04/tiles/subscribe.png', 'every subscribe', 'thanks for watching')]))
