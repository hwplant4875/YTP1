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
if os.environ.get('INTRO'): exec(open(D + 'intro/intro_shots.py', encoding='utf-8').read())   # owner 11/17: intro A-D comparison
else: X.append(sec('s00', [
  (0, 'c2_painting', 136.97, -1.7),  # 136.5-136.93 is a dark, barely visible Valak face from the previous shot (hard cut at 136.95); the bright face runs 136.97-138.70. s04 'survival rate' c2_painting 137.2-138.8 is now the same moment: s04 needs another span
  ('will burn you alive', 'co_burn_4k', 157.5, -0.7, 'a=-18'),  # Father Noiret burning, his head and arms inside the flames; hard cut at 158.2 to an all-fire shot (the old span crossed it)
  ('in midair', 'co_burn_4k', 154.9, -1.1),  # cut at 156.03 to a boy in the pews
  ('bury you alive', 'co_buried_b', 102.4, -3.4),  # one shot 99.5-105.85, but the lighter is only lit from ~102.4 (100-102 is near-black)
  ('snap your neck', 'n2_deliv', 137.71, -0.7),  # v1.2 lore fix: Last Rites has NO neck snap. The Nun II: delivery girl seized by the throat by unseen Valak, choking close-up 137.70-138.42 (frames checked 11/15; 137.27-137.65 lamp wide of the grab, 138.45 cut to her feet dangling off the floor, 139.8 cut to another scene). Near-still face, ~0.55x ok  # Last Rites: hands seize Heather's throat and head from behind, one shot 255.8-260.8+ (B1b: clearer than n2_deliv 137.8; letterboxed, z 1.25 keeps 640 rows)
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
        if ov[3] < 900 and ov[3] - b <= 0.6: b = ov[3]   # owner 11/17 intro review: a short caption-less gap read as a picture pop, so hold to the next caption
        ov[2], ov[3] = (fr(ov[2]) if ov[2] > 0 else 0.0), (fr(b) if b < 900 else b)
X[-1]['vfade'] = {'out': 0.2}


# ==== v2 (11/18, script_v2.md): every line's shot picked from qa/scene_library_v2.md (all 174 clips scanned by eye every 2 s) and the
# story expert's proof moments (story_review_v2.md s4). Rules: the right FILM, no source span used twice (also not across re-uploads of
# the same footage), no suicide act, no worst-gore frame, a fresh shot every 2-3 s. Library gaps are marked WEAK in the comment. ====

# ---- s01 rules: the demo card covers the right half from frame 0, so every shot keeps its subject left (L) ----
X.append(sec('s01', [
  (0, 'ach_room', 44.0, -8.0, 'z=1.35'),                   # ACH: Daniela among the cursed artifacts, dark
  ('is in your room', 'ach_hands', 2.0, -10.0, L),         # ACH: Judy asleep in her bed at night (0:00-0:13)
  ('and it wants you', 'n2_deliv', 126.2, -3.2, L),        # Nun II: Valak at the end of a hallway that turns red
  ('and every one is different', 'c2_grave', 118.82, -5.2, 'z=1.5,dx=320'),  # C2: Janet on the sofa
  ('one is a doll', 'ach_devil_cz', 298.32, -1.3, 'z=1.35,dx=-249,g=1.4'),  # ACH: Judy's hand on the glass, Annabelle inside
  ('wakes up every cursed', 'ach_room', 298.5, -20.0, L),  # ACH: the haunted TV shows Daniela a moment ahead of her (4:58-5:22)
  ('one wants you to give', 'a14_baby', 35.88, -1.4, 'z=1.35,dx=-249'),  # Annabelle: "her SOUL" scrawled on the nursery ceiling
  ('and one wiped out', 'co_valak0', 93.0, -1.2, o(L, 'g=1.25')),  # The Nun: Valak
  ('an entire abbey', 'n1_pray', 2.15, -1.85, o(L, 'g=1.4')),  # The Nun: nuns praying, Valak at the altar
  ('so we score', 'lr_end', 46.0, -2.8, L),                # Last Rites: Ed walks in
  ('strength', 'co_mother_c', 248.0, -3.0, L),             # Conjuring: sheeted Carolyn's chair in the cellar as it rises (4:08)
  ('intelligence', 'dm_altar', 128.0, -3.5, o(ARL, 'g=1.25')),  # DMMDI: the occultist behind her altar
  ('kill count', 'cr_wheel', 567.12, -1.6, o(L, 'g=1.25')),  # Creation: Samuel's body on the floor, wide
  ('and possession', 'lr_end', 99.43, -2.42, L),           # Last Rites: possessed Judy's bloody grin
  ('take over your body', 'dm_david', 315.93, -1.3, o(L, 'flip=1')),  # DMMDI: possessed David screaming
  ('put it all together', 'spooky_nun', 1112.0, -2.9, L),  # The Nun: Irene with a candle
  ]))
X[-1]['vfade'] = {'in': 0.2}

# ==== v6 (11/19, script_v3.md after the owner-approved re-check): s02-s11 re-voiced; the countdown order is now #4 The Devil Made Me Do It
# (s07), #3 Annabelle: Creation (s08), #2 The Nun (s09), #1 The Nun II (s10). Each film's shot list moved with it and was re-anchored to
# the new word timings; every changed line got a true shot from qa/scene_library_v2.md, frame-checked on its source clip. ====

# ---- s02 #9 Annabelle Comes Home (95%) ----
X.append(sec('s02', [
  (0, 'ach_case', 61.0, -2.0),                             # the Annabelle doll grinning on the back seat (1:01-1:03)
  ('this annabelle is the weakest', 'ach_hands', 51.4, -1.6),  # the doll seen through the blue lamp lens (0:51.4-0:53)
  ('because even when it gets loose', 'ach_room', 12.5, -9.0),  # the samurai armor in the dark artifact room (0:12-0:22)
  ('wakes up every cursed object', 'ach_cz_stabs', 100.0, -3.2, 'g=1.25'),  # the typewriter typing "miss me?" by itself (1:40-1:43)
  ("in the warrens' house", 'ach_room', 212.5, -10.0),     # a ghost hand plays the piano beside Daniela's (3:32-3:43)
  ("it doesn't manage to kill", 'ach_case', 152.5, -3.0, 'g=1.25'),  # Ed and Lorraine standing together, alive, after the truck (2:32-2:35)
  ('the ferryman chases', 'ach_ferry', 118.0, -3.0, 'g=1.4'),  # coin-eyed souls, the Ferryman's skull face by the lantern (1:58-2:01) WEAK: small and dark
  ('the babysitter', 'ach_ferry', 126.5, -7.5, 'g=1.25'),  # Mary Ellen runs down the hall with the flashlight (2:06-2:14)
  ('the bride takes over', 'ach_cz_stabs', 209.0, -2.0, 'g=1.25'),  # the Bride face to face with Daniela (3:29-3:31; cut before the blood at 3:31)
  ('her friend', 'ach_devil_cz', 146.0, -6.0),             # possessed Daniela in the Bride's veil (2:26-2:32)
  ('and a hellhound claws', 'ach_wolf', 43.0, -7.0),       # claws rake the car and tear through the convertible roof (0:43-0:50)
  ('with the little girl inside', 'ach_wolf', 20.0, -20.0),  # Judy inside the car, terrified (0:16-0:42)
  ('the doll turns up', 'ach_hands', 32.0, -2.0),          # v6: under the sheet, the doll lying right beside Judy in her bed (0:32-0:34)
  ('and later the demon behind it', 'ach_hands', 74.0, -2.0),  # v6: the horned demon's silhouette over Judy's bed in the red lamp light (1:14-1:16)
  ('tries to take her soul', 'ach_end', 14.0, -3.0, 'g=1.25'),  # v6: the horned demon draws the soul-mist out of Judy's mouth (0:14-0:17)
  ('in the end', 'ach_devil_cz', 324.0, -5.5),             # the three girls in the artifact room after it is over (5:24-5:30)
  ('beat it on their own', 'ach_end', 62.0, -2.0, 'g=1.25'),  # Judy and Mary Ellen pressed against the case, Annabelle behind the glass
  ('by forcing the doll', 'ach_end', 45.0, -3.0, 'g=1.25'),  # the doll in the case, Mary Ellen shoves the glass door (0:45-0:48)
  ('and locking it', 'ach_end', 80.0, -2.0, 'g=1.25'),     # the key turns in the case lock, Daniela's cuff (1:20-1:22)
  ('even loose in your room', 'ach_hands', 54.0, -9.0, L),  # Judy in her room in the lamp's coloured light (0:54-1:03)
  ("but you'll almost certainly", 'ach_end', 95.0, -4.0, o(L, 'g=1.25')),  # Judy close, calm (1:35-1:39)
  ('survival rate', 'ach_case', 149.0, -2.5, o(L, 'g=1.25')),  # the doll alone on the back seat (2:29-2:31.5)
  ]))

# ---- s03 #8 Annabelle (80%) ----
X.append(sec('s03', [
  (0, 'a14_wb_want', 52.0, -9.0),                          # the Annabelle doll in the nursery cabinet, close (0:52-1:01)
  ('this demon is more dangerous', 'a14_cz_soul', 36.0, -2.0),  # the old man in the hall turns: a demonic face (0:36-0:37)
  ("because it doesn't just scare", 'a14_cz_soul', 44.0, -7.0),  # the stereo and record player switch on by themselves (0:44-0:51)
  ('it hurts you', 'a14_cz_attic', 193.4, -1.6),           # fresh claw scratches on Mia's forearm (3:13.4-3:15)
  ('inside your own home', 'a14_cz_soul', 112.0, -1.8),    # the nursery, trashed (1:12-1:13)
  ('it sets your kitchen', 'a14_fire', 87.2, -2.2, AR),    # the popcorn bursts into flames across the stove (1:27.2-1:29.4)
  ('and hurls a priest', 'a14_wb_want', 326.3, -1.6),      # Father Perez hurled backwards off the church steps (5:26.3-5:27.9)
  ('at the door of his own church', 'a14_wb_want', 328.0, -3.0),  # the church's open door after (5:28-5:31)
  ('but it has one big weakness', 'a14_wb_want', 92.0, -3.0),  # the doll close on the chair (1:32-1:35)
  ('in this whole movie', 'a14_cz_soul', 248.0, -3.2),     # v6: the demon takes baby Leah, sliding her out of the doorway into the dark, unhurt (4:08-4:11)
  ('it never kills anyone', 'a14_cz_attic', 306.14, -0.68),  # v6: the horned demon upside down over the stairwell rail above Mia (5:06.14-5:06.43), then Mia fleeing (to 5:06.8)
  ('with its own hands', 'a14_cz_attic', 320.0, -1.6),     # v6: its claw marks on Mia's forearm, she is alive (5:20-5:21.6)
  ('five people die', 'a14_cz_invasion', 336.0, -3.0),     # Annabelle Higgins, the cult girl, holding the doll (5:36-5:39; no blood)
  ('but four of them die', 'a14_cz_invasion', 388.3, -1.4),  # v6: the cultist Annabelle Higgins lunges at Mia (6:28.3-6:29.7; no blood, never 6:30+)
  ('at human hands', 'a14_cz_invasion', 415.6, -1.6),      # v6: the cultist grinning in the nursery doorway (6:55.6-6:57.2; no blood, no killing)
  ('and the only life the demon', 'a14_wb_baby', 292.0, -7.0),  # the life-size Annabelle figure at the window (4:52-4:59)
  ("is evelyn's", 'a14_cz_soul', 480.0, -1.9),             # v6: Evelyn kneeling by John and Mia, close (8:00-8:01.9; John and Mia before and after)
  ('when she gives up', 'a14_cz_soul', 510.0, -5.5),       # Evelyn in the open window holding the doll, her decision (8:30-8:35.5; never 8:36+)
  ('it will burn your home', 'a14_fire', 108.0, -3.5, ARL),  # the kitchen engulfed, Mia small in the doorway (1:48-1:51)
  ('and throw you across the room', 'a14_wb_want', 276.5, -4.5, L),  # v6 NEEDS REWORD: nobody is thrown across a room in any clip (Perez's throw is used above); the doll's face on the car seat (4:36.5-4:41)
  ('but it has never taken', 'a14_cz_soul', 160.5, -3.0, L),  # v6: the doll alone in the living-room armchair (2:40.5-2:43.5)
  ("so you'll probably live", 'a14_cz_attic', 0.0, -7.0, L),  # Mia lays Leah safely in her crib (0:00-0:07)
  ('survival rate', 'a14_wb_want', 44.0, -7.0, L),         # the doll seated in the cabinet (0:44-0:51)
  ]))

# ---- s04 #7 The Conjuring (65%) ----
X.append(sec('s04', [
  (0, 'c1_sheets', 22.8, -4.3),                            # the farmhouse, a sheet flying off the line onto the house
  ('this demon is far', 'co_mother_c', 288.0, -2.0, 'g=1.25'),  # Roger close to unmasked possessed Carolyn, grey skin (4:48-5:12)
  ("because it doesn't need", 'c1_cz_annstory', 31.0, -15.0),  # the Annabelle doll, extreme close-up (Conjuring 2013 prologue)
  ('it gets inside your body', 'c1_dog_b', 310.0, -2.0, 'g=1.4'),  # the dark figure dropping onto Carolyn in bed (5:10-5:12)
  ("and moving out won't", 'c1_dog_b', 368.0, -2.0),       # the family leaves the house (6:08-6:10)
  ('bathsheba was a witch', 'c1_bedroom', 110.5, -1.5, 'g=1.4'),  # Bathsheba crouched on top of the wardrobe, then lunging (1:50.5-1:52)
  ('who gave her own baby', 'c1_land', 84.5, -4.5, 'z=1.35,dy=-140'),  # the old album photo of a baby and a woman (1:24-1:29); the zoom keeps the burned-in subtitle out
  ('and she curses anyone', 'c1_dog_b', 14.75, -3.5),      # the Perrons unloading at the farmhouse
  ('she stops every clock', 'c1_dog_b', 74.5, -3.0),       # the grandfather clock stopped at 3:07 (1:14.5-1:17.5)
  ('leaves bruises on you', 'c1_cz_hideclip', 13.0, -3.0),  # bruises on Carolyn's arm and shoulder at the mirror (0:13-0:16)
  ('while you sleep', 'c1_dog_b', 56.0, -2.0),             # Carolyn's bruised legs as she sits on the bed (0:56-0:58)
  ("yanks the girls' feet", 'c1_sleep', 1.9, -1.1, 'g=1.4'),  # v6: Christine asleep, her leg jerked toward the foot of the bed (0:02.3-0:02.8)
  ('and drags one across', 'co_mother_b', 362.0, -5.0, 'g=1.25'),  # v6: Nancy dragged across the floor, then her hair yanked straight up (6:02-6:07)
  ('and on the very first', 'c1_dog_b', 24.5, -2.0),       # Sadie on the porch, refusing to go in (0:24-0:29)
  ('the family dog is found', 'c1_dog_b', 54.0, -2.0, 'z=1.2,dx=160,dy=80'),  # MORNING: Sadie lying dead in the yard, Carolyn holding April, Roger running in (0:54-0:56)
  ('then she takes over', 'co_mother_c', 292.2, -1.0, 'g=1.4'),  # possessed Carolyn laughing
  ('the mother carolyn', 'co_mother_c', 300.35, -1.35, 'g=1.4'),  # possessed Carolyn grinning
  ('completely', 'universe', 477.5, -2.0, C1),             # Carolyn held down by the men, screaming
  ('and makes her try', 'universe', 445.8, -2.3, C1),      # possessed Carolyn with the scissors over her daughter
  ('the perrons only survive', 'c1_dog_b', 474.0, -6.0),   # Carolyn hugs April; the family safe in the yard (7:54-8:00)
  ('because lorraine reaches', 'universe', 694.2, -1.45, C1),  # Lorraine close, in tears, talking to Carolyn
  ('with a happy memory', 'universe', 698.8, -0.6, C1),    # the mother in red running on the beach with her girl
  ('and ed does the exorcism', 'co_mother_c', 10.0, -5.0),  # Ed reads the rite in the cellar
  ('she will follow you', 'c1_cz_clap', 290.0, -3.0, L),   # Carolyn lit by her match in the cellar (4:50)
  ('and climb inside you', 'c1_exorcism_b', 92.0, -6.0, L),  # Ed's hand on possessed Carolyn's forehead, screaming (1:32-1:38)
  ('but in her own movie', 'c1_exorcism_b', 120.0, -6.0, o(L, 'g=1.25')),  # Carolyn, freed, crawls to April; the hug, every Perron alive (2:00-2:06)
  ('survival rate', 'universe', 715.6, -2.5, o(C1, 'z=1.35')),  # possessed Carolyn screaming
  ]))

# ---- s05 #6 The Conjuring 2 (55%) ----
X.append(sec('s05', [
  (0, 'universe', 1086.0, -2.55, C2),                      # Janet on the sofa
  ('this is the movie that introduced', 'c2_painting', 203.0, -2.4),  # the Valak painting
  ('and valak is much smarter', 'c2_painting', 58.2, -4.0),  # Lorraine with Valak looming behind her
  ('even though nobody in the haunted', 'c2_cz_finale', 528.0, -5.0),  # aftermath: Peggy hugs Janet, everyone alive (8:48-8:53)
  ('it hides behind', 'c2_vision', 56.0, -1.3),            # Valak standing right behind Bill Wilkins in his chair (0:56-0:57)
  ('bill wilkins', 'c2_vision', 2.0, -10.0),               # Bill Wilkins's ghost in his chair (0:00-0:55)
  ('so everyone thinks', 'c2_cz_billy', 186.0, -6.0),      # the BBC sofa interview, Janet in the old man's voice (3:06-3:23)
  ("it blocks lorraine's", 'c2_cz_vision', 372.0, -2.4),   # Valak in the mirror choking Lorraine in her Amityville vision (6:12-6:23; never 6:24+)
  ('throws janet out of her bed', 'c2_cz_voices', 473.0, -1.4, 'g=1.4'),  # v6: Janet in her red pyjamas flung through the air of her bedroom (7:53-7:54.4)
  ('at night', 'c2_cz_voices', 388.5, -3.0, 'g=1.4'),      # v6: Janet waking on the floor at night, out of her bed (6:28.5-6:31.5)
  ('and takes over her body', 'c2_janet', 220.3, -1.1),    # possessed Janet's face
  ('completely', 'c2_cz_billy', 242.0, -5.0),              # possessed Janet in Bill's chair (4:02-4:07)
  ('ed has to fight', 'c2_cz_finale', 18.0, -4.0, 'g=1.25'),  # Ed thrown back by wind and debris in the house (0:18-0:23)
  ('but valak has one', 'c2_cz_finale', 226.8, -2.5),      # Lorraine's Bible, the name VALAK scratched into the page (3:46.8-3:49.3)
  ('if you know its name', 'c2_name_b', 58.3, -1.65, AR),  # Lorraine bent over the Bible
  ('and lorraine sends it', 'c2_name', 43.82, -3.0, AR),   # Lorraine pinned, shouting
  ("it's smarter than you", 'c2_name', 55.695, -2.0, ARL),  # Valak's demon face, pulled away
  ('fool everyone you call', 'c2_cz_finale', 24.0, -7.0, L),  # the neighbour with an axe, Lorraine at the door in the rain (0:24-0:31)
  ('but in its whole movie', 'c2_cz_finale', 495.0, -4.0, L),  # v6: aftermath, Lorraine alive on the wrecked floor (8:15-8:19)
  ('it never kills a single', 'c2_cz_finale', 500.0, -4.0, L),  # v6: Vic and Lorraine in the wrecked room, everyone alive (8:20-8:24)
  ('and the moment someone says', 'c2_cz_finale', 232.3, -1.0, L),  # v6: the VALAK page in Lorraine's Bible, a second look (3:52.3-3:53.3)
  ("it's sent straight back", 'c2_cz_finale', 459.3, -1.7, L),  # v6: Valak screams and is pulled backward into the dark (7:39.3-7:41)
  ('survival rate', 'c2_painting', 189.6, -4.2, 'z=1.5,dx=320'),  # Valak's face over Lorraine's shoulder
  ], inserts=[
    ins('you have power over it', 1.97, 'film', shots=[(0, 'c2_name', 39.75, 1.0, o(AR, 'lufs=-17'))], sub='You are Valak.'),
    ins('just by saying it', 2.13, 'film', shots=[(0, 'c2_name', 52.81, 1.0, o(AR, 'lufs=-17'))], sub='I condemn you back to hell.'),
  ]))

# ---- s06 #5 Last Rites (45%) ----
X.append(sec('s06', [
  (0, 'lr_family', 102.2, -3.95),                          # the Smurl street at night
  ('this demon is stronger', 'lr_end', 42.0, -3.0),        # the ornate mirror, glowing
  ('than that valak', 'c2_painting', 206.88, -0.75),       # callback: Valak (Conjuring 2)
  ("and it's the only one", 'lr_s01_baby', 18.3, -2.6),    # v6: 1964, Lorraine's reflection in the mirror smiles evilly at her (0:18.3-0:20.9; never 0:21+)
  ('that has ever left a warren', 'lr_birth', 55.0, -6.0), # v6: the still newborn laid on Lorraine's chest (0:55-1:01)
  ('even if only for a moment', 'lr_birth', 104.5, -3.0),  # v6: warm light, the baby starts crying, revived (1:44.5-1:47.5)
  ('it lives inside an old mirror', 'lr_s01_baby', 2.0, -7.0),  # the old mirror (0:00-0:10; never 0:21-0:23)
  ('and in nineteen sixty-four', 'lr_birth', 20.05, -10.0, 'g=1.4'),  # Lorraine in labour
  ('judy warren was born dead', 'lr_birth', 41.0, -5.0),   # the silent newborn (0:40-0:47)
  ('because of it', 'lr_s01_baby', 141.3, -0.75, 'g=1.25'),  # v6: the lightning flash, the barefoot mirror entity in a gown crouched over Lorraine's bed (2:21.3-2:22.05; dark before and after)
  ('until ed and lorraine prayed', 'lr_birth', 76.0, -6.0),  # v6: Lorraine praying, Ed's hand on her face (1:16-1:22)
  ('her back to life', 'lr_birth', 117.0, -6.0),           # v6: Lorraine holds the crying newborn (1:57-2:03)
  ('twenty-two years later', 'lr_judy', 50.0, -6.5),       # adult Judy in the mirror maze of brides
  ('it hides behind three', 'lr_cz_comp', 92.0, -1.5),     # the old woman ghost under the wedding dress (1:32-1:33)
  ('three ghosts', 'lr_axe', 234.75, -0.8),                # a ghost's face lunging at the camera
  ('makes a girl cough', 'lr_s03_blood', 171.0, -1.2),     # Dawn at the sink with the family, wide (2:51; never the close-ups)
  ('blood and broken glass', 'lr_s03_blood', 200.0, -1.6),  # Heather's horrified face (3:20-3:21.6; never the sink close-up at 3:18)
  ('drives the priest', 'lr_priest', 31.0, -3.7),          # Father Gordon alone at his desk
  ('to his death', 'lr_priest', 138.45, -1.95),            # fire in his glasses (never 2:22-2:37)
  ('locks lorraine in the basement', 'lr_exorcism', 4.0, -9.0, 'g=1.4'),  # v6: Lorraine lying on the basement floor (0:04-0:13) WEAK: dark
  ('and takes over judy', 'lr_s09_possessed', 100.0, -1.2),  # possessed Judy, white eyes, bloody mouth (1:40-1:41)
  ('and makes her hang herself', 'lr_s09_possessed', 40.2, -3.3),  # v6: possessed Judy crawling on all fours across the bedroom (0:40-0:43); no rope, no attic, never 2:44+
  ('until ed cuts her down', 'lr_exorcism', 261.5, -3.5),  # v6: Ed in the candlelight after (4:21.5-4:25; after the attic, no rope; never 2:40-4:15)
  ("and she's brought back", 'lr_exorcism', 311.3, -1.1, 'g=1.25'),  # v6: Lorraine bent over Judy, praying, backlit by the stair rails (5:11.3-5:12.4; the mirror faces cut in at 5:13)
  ('a second time', 'lr_exorcism', 318.6, -4.4),           # v6: Judy opens her eyes, held by Lorraine (5:18.6-5:23)
  ("ed's exorcism doesn't", 'lr_end', 24.0, -3.0),         # Ed reading the rite, hand raised
  ('even work', 'lr_end', 80.8, -1.0),                     # the Bible burns in Ed's hands
  ('and only the whole family', 'lr_end', 166.0, -9.0),    # three pairs of hands on the mirror (2:46-2:55)
  ('can break the mirror', 'lr_end', 183.0, -1.2),         # the mirror's ghosts screaming against the cracking glass (3:03)
  ('throwing the mirror away', 'lr_s03_blood', 102.0, -8.0, L),  # the mirror thrown into the garbage truck (1:42-1:50)
  ('and neither will a priest', 'lr_priest', 2.0, -12.0, L),  # Father Gordon (0:00-0:15)
  ('but it only takes two lives', 'lr_priest', 122.5, -4.0, L),  # v6: Father Gordon by his match flame, before his death (2:02.5-2:06.5)
  ('and the one it possessed', 'lr_end', 202.5, -5.0, L),  # v6: Judy close, in tears, free (3:22.5-3:27.5)
  ("so you've got close", 'lr_end', 226.0, -7.0, L),       # v6: aftermath on the landing, Ed standing (3:46-3:53)
  ('survival rate', 'lr_judy', 232.0, -2.0, 'z=1.6,dx=360'),  # Judy's demonic grin in the cracked mirror
  ]))

# ---- s07 #4 The Devil Made Me Do It (35%) (v5: s08 #3) ----
X.append(sec('s07', [
  (0, 'dm_promise', 19.85, -3.2, AR),                      # the occultist Isla
  ('this one is smarter', 'dm_calvary', 64.0, -6.0, AR),   # Isla and Lorraine face to face in the dark (1:04-1:10)
  ("because it doesn't have to kill", 'co_stab', 104.0, -3.0),  # Isla's face, clearest (1:44-1:47)
  ('it makes you do it', 'dm_david', 301.12, -2.0),        # Arne on the floor, the demon in him
  ('a witch hides a cursed charm', 'dm_cz_nightmare', 418.0, -1.5, 'g=1.25'),  # the witch's totem under the house (6:58-6:59)
  ('in your home', 'dm_cz_nightmare', 430.0, -9.0),        # Lorraine photographs the totem (7:10-7:19)
  ('and from then on', 'dm_bruno_b', 30.0, -10.0),         # Arne at the party, before
  ('the killer is you', 'dm_bruno_b', 156.3, -0.8),        # the knife on the floor
  ('arne johnson stabs', 'dm_bruno_b', 144.44, -1.3),      # Bruno dancing to "Call Me", just before
  ('his landlord', 'dm_cz_archie', 60.0, -8.0),            # Bruno, the landlord, in daylight (0:56-1:09)
  ('twenty-two times', 'dm_bruno_it', 208.5, -4.0),        # Arne on the road after, dazed (3:28.5-3:32.5)
  ('a girl named jessica', 'dm_vision', 102.6, -1.4, o(AR, 'g=1.25')),  # Jessica smiling
  ('stabs her best friend', 'dm_vision', 106.0, -2.0, AR), # Jessica and Katie together (1:42-2:07)
  ('twenty-two times#2', 'dm_vision', 185.47, -0.6, AR),   # the bloody hand with a rosary
  ('and then dies too', 'co_stab', 36.8, -3.2),            # the sheet-covered body in the morgue
  ('the witch kills her own father', 'dm_altar', 52.42, -2.3, AR),  # a ringed hand grips Kastner's head
  ('and turns ed against', 'dm_final', 102.65, -1.1),      # Ed possessed, bleeding eyes
  ('until he nearly kills', 'dm_ar_love', 0.0, -6.0, AR),  # Ed swings the sledgehammer at Lorraine in the tunnel (0:00-0:06)
  ('and when the witch fails', 'dm_promise', 40.0, -1.2, AR),  # Isla twisted by her demon, wide (0:40-0:41)
  ('her own demon twists', 'dm_promise', 58.0, -6.0, AR),  # Isla collapsing (0:58-1:04; never 0:56-0:57)
  ("you can't fight it", 'dm_cz_herself', 31.0, -12.0, L),  # Isla attacks Lorraine with a knife (0:31-0:43)
  ('because the hands holding', 'dm_vision', 186.2, -1.5, ARL),  # the bloody knife in the hay
  ('and only smashing', 'dm_ar_love', 104.0, -10.0, ARL),  # Ed smashes the witch's altar (1:44-1:54)
  ('survival rate', 'dm_promise', 49.5, -4.0, ARL),        # Isla's pale face in the dark
  ], inserts=[
    ins('the killer is you', 1.1, 'film', shots=[(0, 'dm_david', 319.77, 1.0, 'lufs=-17')], sub='Take me!'),
  ]))

# ---- s08 #3 Annabelle: Creation (25%) (v5: s07 #4) ----
X.append(sec('s08', [
  (0, 'cr_sam', 29.3, -7.7),                               # the Annabelle doll in a chair, bright
  ('this is where the annabelle', 'cr_wasnt', 0.0, -2.6),  # Bee at her tea table with the doll
  ("and it's even more violent", 'cr_scarecrow', 26.0, -10.0),  # the scarecrow (0:26-0:52)
  ("because it doesn't need", 'cr_well', 96.0, -5.0),      # v6: its own hand grabs Linda and pulls her over the well's rim (1:36-1:41)
  ('it kills people itself', 'cr_trapped', 350.0, -3.0),   # possessed Janice lunges with a knife (5:50-5:53)
  ('it pretends to be bee', 'cr_esther_scenes', 136.0, -6.0),  # Bee at the tea table (2:16-2:22)
  ('the dead daughter', 'cr_esther_scenes', 60.0, -6.0),   # the Mullins at dinner before (flashback, 0:58-1:04)
  ('so her heartbroken parents', 'cr_wasnt', 39.1, -2.95),  # Esther, grieving
  ('let it into the doll', 'cr_wasnt', 60.8, -2.2),        # the doll's face, sinister
  ('then it goes after', 'cr_sam', 37.8, -5.2),            # Sister Charlotte and the orphans unloading the truck
  ('it comes for janice', 'cr_rt_chair', 38.0, -10.0, 'g=1.4'),  # Janice on the stairlift riding up in the dark (0:36-0:58)
  ('and leaves her in a wheelchair', 'cr_stair', 1.0, -5.0),  # Janice in her wheelchair in the sun, eyes closed (0:00-0:06)
  ('then wheels her into a barn', 'cr_stair', 30.0, -9.0),      # the hooded "Charlotte" wheels Janice across the field into the barn (0:24-0:39)
  ('and takes over her body', 'cr_stair', 125.6, -2.0),    # the black bile forced into Janice's mouth
  ('through her it snaps', 'cr_sam', 16.0, -3.0),          # Samuel's fingers bend back around the crucifix (cut by 0:19)
  ('and kills him', 'cr_sam', 59.8, -1.2),                 # his body on the floor, wide
  ('then it tears his wife', 'cr_esther_scenes', 78.0, -6.0, 'g=1.25'),  # Esther in the dark (1:18-1:24); her death is voiced only, never shown
  ('and twelve years later', 'cr_end', 9.05, -5.95),       # the Higgins photos
  ('through janice and her cultist', 'cr_end', 46.0, -2.0, 'z=1.25,dx=-200'),  # v6: grown Janice in white and her bearded cultist boyfriend at the Higgins' bedroom door (0:46-0:48); the zoom keeps the wall's red smear at the right edge out of frame
  ('it kills the couple', 'cr_end', 19.0, -3.3),           # the Higgins couple woken in bed
  ('who adopted her', 'cr_end', 37.3, -1.5),               # Pete Higgins at the bedroom door, seen from behind, before the attack (0:35.5-0:38.9); the knife enters at 0:39.0, never past 0:38.8
  ('a nun and five girls', 'cr_well', 116.4, -3.2),        # Sister Charlotte holding Linda in the field
  ('but only because the nun locks', 'cr_trapped', 372.0, -10.0),  # Charlotte shoves Janice and the doll into the closet, door slams (6:12-6:22)
  ('and the demon stays', 'cr_trapped', 256.3, -5.5),      # possessed Janice, a sly smile, holding a doll
  ("it doesn't want to scare you", 'cr_cz_orphan', 156.0, -20.0, L),  # possessed Janice walking upright (2:36-2:56)
  ('and it never gives', 'cr_soul', 140.6, -7.8, 'z=1.2,dx=-160'),  # Janice on the dark landing
  ('survival rate', 'cr_cz_released', 264.0, -10.0, L),    # the doll in the closet lined with Bible pages (4:24-4:34)
  ]))

# ---- s09 #2 The Nun (12%) (v5: s10 #1) ----
X.append(sec('s09', [
  (0, 'co_valak0', 4.0, -7.5),                             # Valak rising out of the water
  ('this is valak', 'spooky_nun', 1049.3, -5.0, 'g=1.4'),  # Valak
  ('loose from a doorway', 'spooky_nun', 1117.8, -2.5, 'g=1.4'),  # the "Finit hic Deo" door
  ('to hell', 'spooky_nun', 1092.45, -0.6),                # Valak roaring
  ('under an abbey in romania', 'n1_hl_abbess', 216.0, -2.0),  # the abbey at dusk (3:36-3:38)
  ('before irene even arrives', 'n1_open', 38.0, -1.4, AR),  # the nun in the corridor, screaming (never 1:16+)
  ('every nun in the abbey', 'spooky_nun', 999.0, -7.0, 'g=1.4'),  # overhead: the dead nuns
  ('and the sisters she prays', 'n1_pray', 21.0, -7.3),    # Irene praying among the nuns
  ('were never really there', 'n1_pray', 39.0, -20.0, 'g=1.4'),  # the empty habits on the floor
  ('it buries father burke', 'co_buried_b', 75.6, -2.4, 'g=1.25'),  # Burke in the coffin with his lighter
  ('in a coffin', 'co_buried_b', 98.0, -1.5, 'g=1.25'),    # Burke pulls the bell string in the coffin (1:38-1:48)
  ('and it drowns irene', 'co_valak0', 26.1, -1.6, 'g=1.4'),  # Irene held under the water
  ('and frenchie has to pump', 'n1_cz_possessed', 461.8, -2.0),  # Frenchie bent over Irene, pumping her chest (7:41.8-7:43.8)
  ('to bring her back', 'n1_cz_possessed', 469.0, -4.0),   # Frenchie breathing into her, she comes back (7:49-7:53)
  ('the church sent', 'co_valak0', 64.0, -1.0, 'g=1.4'),   # the relic in Irene's hands
  ('a priest', 'spooky_nun', 317.2, -0.65, 'g=1.4'),       # Father Burke
  ('and a nun', 'spooky_nun', 1080.42, -1.15, 'g=1.4'),    # Irene
  ('they found the actual blood', 'co_valak0', 84.65, -1.6, 'g=1.25'),  # the vial of Christ's blood on its chain
  ('in the abbey#2', 'n1_cz_fight', 284.0, -1.5),          # the vial held up in the flooded crypt (4:44)
  ('and even then', 'co_valak0', 96.5, -1.45, 'g=1.4'),    # Valak's face soaked in the blood
  ('hiding inside frenchie', 'co_valak0', 168.35, -2.05),  # WEAK: Frenchie (the escape into him is in no clip)
  ('it wiped out a whole abbey', 'n1_pray', 47.0, -10.0, L),  # overhead: the empty habits on the chapel floor (0:47-0:57)
  ('and the three people who lived', 'n1_hl_abbess', 3.0, -5.0, L),  # v6: Burke, Irene and Frenchie walk into the candle-lit hall of tombs (0:03-0:08)
  ('only made it because', 'n1_ar_defeats', 134.3, -1.2, ARL),  # v6: Irene, the blood of Christ in her mouth, takes hold of Valak (2:14.3-2:15.5)
  ('the actual blood of christ#2', 'co_valak0', 98.2, -1.5, o(L, 'g=1.25')),  # v6: the blood of Christ bursts red over the water around Valak (1:38.2-1:39.7)
  ('so alone in your room', 'co_valak0', 118.0, -3.2, o(L, 'flip=1')),  # Valak clawing
  ('survival rate', 'co_valak0', 87.2, -3.2, L),           # Valak close-up holding the vial
  ]))

# ---- s10 #1 The Nun II (5%) (v5: s09 #2) ----
X.append(sec('s10', [
  (0, 'n2_maurice', 160.5, -8.9),                          # Valak's silhouette
  ('this is valak at its strongest', 'n2_exorcise', 2.0, -1.1),  # Valak's snarl
  ('stronger than any demon', 'n2_lucy', 3.45, -2.0),      # Valak, glowing eyes
  ("it's hunting for the eyes", 'n2_cz_returns', 46.6, -1.2),  # the Saint Lucy reliquary held up, its rim glowing (0:46.6-0:47.8)
  ('a holy relic', 'co_neck_b', 191.9, -0.5, 'g=1.25'),    # the reliquary held in two hands
  ('that would make it', 'n2_lucy', 9.5, -1.25),           # Valak
  ('and it has been hiding', 'n2_maurice', 38.5, -4.8, 'g=1.4'),  # Maurice (Frenchie) possessed
  ('the man who saved irene', 'n2_maurice', 118.5, -6.0, 'g=1.4'),  # Maurice grinning, possessed
  ('it lifts a priest', 'n2_burn', 370.5, -1.5),           # Father Noiret rises above the altar (6:10.5-6:12; s00 holds 372.1-373.2)
  ('and burns him alive', 'n2_burn', 376.35, -0.95),       # Jacques screams as Noiret burns above him, lit by the fire (6:16.35-6:17.3; s11 holds 6:17.35-6:18.2)
  ('snaps the neck', 'n2_deliv', 138.5, -1.2),             # the delivery kid lifted by the throat, feet dangling (2:18.5-2:19.7; cut before the snap)
  ('of a kid making', 'n2_deliv', 47.0, -3.0),             # the delivery kid in a cap at the shelves, earlier (0:47-0:50)
  ('kills the headmistress', 'n2_altar', 89.0, -0.95, 'g=1.4'),  # Madame Laurent
  ('of a boarding school', 'n2_cz_goat', 283.5, -2.5, 'g=1.25'),  # the school dormitory, rows of schoolgirls in nightgowns with Sister Debra between the beds (4:43-4:46.5)
  ('sister irene only survives', 'n2_lucy', 24.0, -1.75),  # Irene in mid-air above the fire
  ('being set on fire', 'n2_lucy', 41.1, -1.45),           # Irene burning in mid-air
  ('because she comes from', 'n2_exorcise', 75.0, -2.5),   # little Irene in her mother's arms (1:15-1:17)
  ('and it takes a miracle', 'n2_lucy', 50.0, -1.4),       # Irene unhurt as the fire dies
  ('wine turning into', 'n2_exorcise', 86.0, -10.0),       # the wine barrels burst red over Valak (1:26-1:36)
  ('to drive it out', 'n2_exorcise', 102.0, -2.0),         # Valak goes up in a column of fire (1:42-1:44)
  ('it burned a priest alive', 'n2_burn', 378.3, -1.1, L), # v6: Noiret's body bursts into a fireball above the altar (6:18.3-6:19.4)
  ('and the only person who ever walked', 'n2_lucy', 30.0, -8.0, 'z=1.15,dx=150'),  # Irene burning in mid-air (0:30-0:38)
  ('was a descendant of saint lucy', 'n2_burn', 136.5, -5.5, L),  # v6: the painting of Saint Lucy in the Tarascon church (2:16.5-2:22)
  ('so for anyone else', 'n2_exorcise', 98.0, -3.0, o(L, 'flip=1')),  # Valak's rotted face
  ('the fire wins', 'n2_exorcise', 122.6, -2.3, L),        # v6: a burst of fire fills the frame (2:02.6-2:04.9)
  ('survival rate', 'n2_exorcise', 23.15, -1.68, L),       # Valak close-up
  ]))

# ---- s11 outro: ACH case-closing footage on the first line, the hide-and-clap scene under the last lines ----
X.append(sec('s11', [
  (0, 'still_posterwall', 1.0, -4.0),                      # all 9 posters (callback to the cold open)
  ('from the doll', 'ach_end', 82.0, -4.0, 'g=1.25'),      # ACH: Mary Ellen, Daniela and Judy together after the lock (1:22-1:26)
  ('locked back in its case', 'ach_end', 93.2, -0.8, 'g=1.25'),  # ACH: Annabelle locked in the case behind Daniela (1:33.2-1:34)
  ('to the valak', 'n2_burn', 373.3, -1.3),                # v6: The Nun II, Jacques in the pews watching Noiret burn above the altar, lit by the fire (6:13.3-6:14.6)
  ('that burned a priest alive', 'n2_burn', 375.5, -0.75), # v6: Noiret burning in the air above the altar, then all fire (6:15.5-6:16.25; s00 holds 374.7-375.4)
  ('in midair', 'n2_burn', 377.35, -0.85),                 # v6: Jacques screaming up at the burning priest (6:17.35-6:18.2; s10 holds 6:16.35-6:17.3)
  ('which one would you least', 'universe', 22.5, -8.5, C1),
  ('tell me in the comments', 'universe', 136.4, -5.6, C1),
  ('i went through every death', 'universe', 151.0, -2.7, C1),
  ("and we're a small channel", 'universe', 153.82, -3.1, C1),
  ('thanks for watching', 'universe', 157.0, -2.6, C1),
  ], inserts=[
    ins('END', 0.72, 'clap', shots=[(0, 'universe', 159.6, 1.0, o(C1, 'lufs=-22'))]),
  ], extra=[('png', '../ep04/tiles/subscribe.png', 'every subscribe', 'thanks for watching'),
            ('word', 'Every Conjuring demon', 'every conjuring demon', 'from the doll')]))
