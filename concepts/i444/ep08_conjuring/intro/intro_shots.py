# EP08 cold-open alternatives A-D (intro/intros_v1.md). shots.py execs this instead of its own s00 when INTRO=A|B|C|D;
# build with VOICE=intro/<V>/voice. Spans come from verified shots elsewhere in shots.py; for the A-D COMPARISON renders a span that
# a later section also uses is allowed (marked DUPE); the winning intro then gets fresh spans before the final render.
V = os.environ['INTRO']
RANK = [("We're ranking", "we're ranking", 'every conjuring demon'), ('Every Conjuring demon', 'every conjuring demon', 'by your chance'),
        ('By your chance', 'by your chance', 'of surviving it')]
POST = ('still_posterwall', 0.0, -5.0)
SH = {
 'A': ([
  (0, 'c2_painting', 136.97, -1.7),                                # Valak's face (same as the old s00 frame 0)
  ('burned a priest alive', 'co_burn_4k', 157.5, -0.7, 'a=-18'),   # Father Noiret burning
  ('in midair', 'co_burn_4k', 154.9, -1.1),
  ('and snapped', 'n2_deliv', 132.72, -0.9),                       # DUPE s09: the delivery girl scrambling on the corridor floor
  ("a girl's neck", 'n2_deliv', 137.71, -0.7),                     # the delivery girl seized by the throat
  ('and it still only made', 'n2_deliv', 126.2, -3.2),             # DUPE s01: Valak at the end of the red hallway
  ('number two', 'n2_exorcise', 23.15, -1.68),                     # DUPE s09: Valak close-up, glowing eyes
  ('number one', 'spooky_nun', 1092.45, -0.6),                     # DUPE s10: Valak roaring close-up
  ('is the same demon', 'c2_painting', 189.6, -4.2, 'z=1.5,dx=320'),  # DUPE s05: Valak's face over Lorraine's shoulder
  ('at full power', 'spooky_nun', 1049.3, -5.0, 'g=1.4'),          # DUPE s10
  ("so we're ranking", *POST),
  ('from a doll', 'ach_case', 62.0, -1.85, 'g=1.4'),               # DUPE s05: the doll alone in the car (297.5 cropped her behind a blurred head and ran 0.44x, looked frozen)
  ('locked back in its case', 'ach_end', 80.3, -0.9),              # DUPE s02: the key turning in the case lock
  ('to the one that wiped out', 'n1_pray', 21.0, -7.3),            # DUPE s10: Irene praying among the nuns, candle-lit (spooky_nun 999 was near-black)
  ], [
  ('This demon', 0, 'burned a priest alive'), ('Burned a priest alive', 'burned a priest alive', 'in midair'),
  ('In midair', 'in midair', 'and snapped'), ("And snapped a girl's neck", 'and snapped', 'and it still only made'),
  ('And it still only made', 'and it still only made', 'number two'), ('Number two', 'number two', 'number one'),
  ('Number one', 'number one', 'is the same demon'), ('Is the same demon', 'is the same demon', 'at full power'), ('At full power', 'at full power', "so we're ranking"),
  ("So we're ranking", "so we're ranking", 'every conjuring demon'), RANK[1], RANK[2], ('Of surviving it', 'of surviving it', 'from a doll'),
  ('From a doll', 'from a doll', 'that two teenagers'), ('That two teenagers', 'that two teenagers', 'locked back in its case'), ('Locked back in its case', 'locked back in its case', 'to the one that wiped out'),
  ('To the one that wiped out', 'to the one that wiped out', 'an entire abbey'), ('An entire abbey', 'an entire abbey', 999)]),
 'B': ([
  (0, 'universe', 904.0, -1.5, C1),                                # the Annabelle doll close-up (The Conjuring prologue)
  ('starts moving on its own', 'ach_devil_cz', 297.5, -0.7),       # laptop: prefer an ACH shot of the doll MOVING by itself if one exists
  ("you'll probably live", 'ach_end', 77.62, -1.65),               # DUPE s02: the girls push the glass door shut
  ('if every clock', 'c1_land', 141.0, -4.5),                      # DUPE s04: the clock stopped at 3:07
  ("you're in real trouble", 'co_mother_c', 305.9, -5.1, 'g=1.4'), # possessed Carolyn grinning
  ('but if a nun', 'n2_deliv', 126.2, -3.2),                       # DUPE s01: Valak at the end of the hallway
  ("it's already too late", 'c2_painting', 136.97, -1.7),          # Valak's face lunges
  ("we're ranking", *POST),
  ], [
  ('If a doll in your house', 0, 'starts moving on its own'), ('Starts moving on its own', 'starts moving on its own', "you'll probably live"),
  ("You'll probably live", "you'll probably live", 'if every clock'), ('If every clock', 'if every clock', 'stops at three oh seven'),
  ('Stops at 3:07', 'stops at three oh seven', "you're in real trouble"), ("You're in real trouble", "you're in real trouble", 'but if a nun'),
  ('But if a nun', 'but if a nun', 'is standing at the end'), ('Is standing at the end', 'is standing at the end', 'of your hallway'),
  ('Of your hallway', 'of your hallway', "it's already too late"), ("It's already too late", "it's already too late", "we're ranking"),
  *RANK, ('Of surviving it', 'of surviving it', 999)]),
 'C': ([
  (0, 'c2_painting', 136.97, -1.7),
  ('a doll that wants your soul', 'universe', 904.0, -1.5, C1),
  ('a witch who turns', 'co_mother_c', 305.9, -5.1, 'g=1.4'),
  ('against you', 'universe', 659.1, -1.8, C1),                    # Carolyn raising the scissors over April
  ('or a curse', 'dm_vision', 102.6, -1.4, o(AR, 'g=1.25')),       # DUPE s08: Jessica smiling
  ('that makes you stab', 'dm_vision', 153.15, -0.85, o(AR, 'g=1.4')),
  ('your best friend', 'dm_vision', 160.0, -0.85, o(AR, 'g=1.25')),
  ('twenty-two times', 'dm_vision', 157.1, -1.8, o(AR, 'g=1.25')),
  ('choose wrong', 'spooky_nun', 1092.45, -0.6),                   # DUPE s10: Valak roaring
  ("and you won't see morning", 'co_burn_4k', 157.5, -0.7, 'a=-18'),
  ("we're ranking", *POST),
  ], [
  ('Which would you rather face?', 0, 'a doll that wants your soul'), ('A doll that wants your soul', 'a doll that wants your soul', 'a witch who turns'),
  ('A witch who turns', 'a witch who turns', 'your own mother'), ('Your own mother', 'your own mother', 'against you'),
  ('Against you', 'against you', 'or a curse'), ('Or a curse', 'or a curse', 'that makes you stab'),
  ('That makes you stab', 'that makes you stab', 'your best friend'), ('Your best friend', 'your best friend', 'twenty-two times'),
  ('22 times', 'twenty-two times', 'choose wrong'), ('Choose wrong', 'choose wrong', "and you won't see morning"),
  ("And you won't see morning", "and you won't see morning", "we're ranking"), *RANK, ('Of surviving it', 'of surviving it', 999)]),
 'D': ([
  (0, 'universe', 904.0, -1.5, C1),
  ('was beaten by two teenagers', 'ach_end', 82.4, -2.2),         # DUPE s02: Mary Ellen, Daniela and Judy side by side
  ('who just shut a glass door', 'ach_end', 77.62, -1.65),         # DUPE s02
  ('another', 'spooky_nun', 1092.45, -0.6),                        # DUPE s10
  ('wiped out an entire abbey', 'n1_pray', 39.0, -20.0, 'g=1.4'),  # DUPE s10: overhead, the empty habits (spooky_nun 999 was near-black)
  ('before anyone even showed up', 'n1_open', 0.0, -8.7, o(AR, 'g=1.8')),  # DUPE s10: the abbey (g 1.8: it was near-black at 1.4)
  ('seven more', 'co_mother_c', 305.9, -5.1, 'g=1.4'),
  ('sit in between', 'dm_vision', 157.1, -1.8, o(AR, 'g=1.25')),
  ("and we're ranking", *POST),
  ], [
  ('One of these demons', 0, 'was beaten by two teenagers'), ('Was beaten by two teenagers', 'was beaten by two teenagers', 'and a little girl'),
  ('And a little girl', 'and a little girl', 'who just shut a glass door'), ('Who just shut a glass door', 'who just shut a glass door', 'another'),
  ('Another', 'another', 'wiped out an entire abbey'), ('Wiped out an entire abbey', 'wiped out an entire abbey', 'of nuns'),
  ('Of nuns', 'of nuns', 'before anyone even showed up'), ('Before anyone even showed up', 'before anyone even showed up', 'seven more'),
  ('Seven more', 'seven more', 'sit in between'), ('Sit in between', 'sit in between', "and we're ranking"),
  ("And we're ranking", "and we're ranking", 'every one of them'), ('Every one of them', 'every one of them', 'by your chance'),
  RANK[2], ('Of surviving it', 'of surviving it', 999)]),
}
X.append(sec('s00', SH[V][0], extra=[('word', w, a, b) for w, a, b in SH[V][1]], clip_db=-22))
