# EP07 v7 shot plan, read by build_edl_v7.py. A shot is (phrase, clip, in_s, -clean_s[, 'opts']).
# opts: L = 'z=1.35,dx=249' moves the subject left of the stat card; 'flip' mirrors the shot.
L = 'z=1.35,dx=249'
# ---- s00 cold open: frame 0 = Pinhead; every chunk gets its own caption and its own lore-exact cut ----
X.append(sec('s00', [(0, 'hr1_pack4k', 34.57, -11.0),                       # 1987 Pinhead, hospital blinds
  ('tear straight', 'hr1_jesuswept', 117.49, -0.67),                       # hook in Frank's shirt
  ('through your flesh', 'hr1_jesuswept', 122.75, -1.5),                   # chains rip his chest
  ('with hooked', 'hr1_jesuswept', 127.21, -2.13),                         # Frank's face torn by the hooks
  ('this one will#1', 'hr9_rev', 2187.05, -1.7),                    # the Priest (2022)
  ('peel your', 'hr9_rev', 2190.3, -2.8),                                 # the Priest raises the blade
  # wire hook pulls Nora's skin
  ("you're still", 'hr9_rev', 2183.7, -3.3),                            # Nora alive, screaming
  ('this one will#2', 'hr3_unstoppable', 106.5, -1.6),                     # Hell on Earth Pinhead
  ('turn you', 'hr3_cenoloose', 145.5, -2.1),                              # Pistonhead
  ('one of his', 'hr3_cenoloose', 105.9, -2.8),                            # Barbie
  ('cenobites', 'hr3_cenoloose', 178.04, -5.0),                            # Camerahead
  ('this one will#3', 'hr5_welcome', 0.0, -1.1),                        # Inferno Pinhead in Thorne's hell
  ('trap you', 'hr5_torment', 420.85, -1.8),                               # chains whip around Thorne
  ('in your own', 'hr5_torment', 425.1, -3.0),                             # Thorne hung in the chains
  ('personal hell', 'hr5_cruelty', 22.0, -1.8),                            # the legless creature of his hell
  ('forever', 'hr5_torment', 450.33, -3.7),                                # Thorne held forever
  ('and they all', 'hr2_tiffvs', 125.5, -3.3),                             # Revelations Pinhead
  ('do it', 'hr3_iamtheway', 126.55, -1.35),                               # Hell on Earth Pinhead
  ('calmly', 'hr1_pack4k', 45.6, -11.5),                                   # the calm 1987 stare
  ("we're ranking", 'still_posterwall', 0.0, -5.0)],
  extra=[('word', w, a, b) for w, a, b in [
    ('This Pinhead will', 0, 'tear straight'), ('Tear straight', 'tear straight', 'through your flesh'),
    ('Through your flesh', 'through your flesh', 'with hooked'), ('With hooked chains', 'with hooked', 'this one will#1'),
    ('This one will', 'this one will#1', 'peel your'), ('Peel your skin', 'peel your', 'off while'), ('Off while', 'off while', "you're still"),
    ("You're still alive", "you're still", 'this one will#2'), ('This one will', 'this one will#2', 'turn you'),
    ('Turn you into', 'turn you', 'one of his'), ('One of his', 'one of his', 'cenobites'), ('Cenobites', 'cenobites', 'this one will#3'),
    ('This one will', 'this one will#3', 'trap you'), ('Trap you', 'trap you', 'in your own'), ('In your own', 'in your own', 'personal hell'),
    ('Personal Hell', 'personal hell', 'forever'), ('Forever', 'forever', 'and they all'), ('And they all', 'and they all', 'do it'),
    ('Do it', 'do it', 'calmly'), ('Calmly', 'calmly', "we're ranking"), ("We're ranking", "we're ranking", 'every pinhead'),
    ('Every Pinhead', 'every pinhead', 'by your chance'), ('By your chance', 'by your chance', 'of surviving'),
    ('Of surviving him', 'of surviving', 999)]], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out (one word 0.9 s, a phrase 1.6 s max); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.6))
# ---- s01 rules (stat card from frame 0) ----
s01_end = vdur('s01') + 0.05
X.append(sec('s01', [(0, 'hr1_pack4k', 62.4, -3.4),
  ('you just', 'hr2_tiffany', 49.59, -9.9),
  ("that movie's", 'hr1_pack4k', 108.4, -2.4, L),
  ('we score', 'hr4_pathway', 125.0, -6.4, L),
  ('intelligence', 'hr4_pathway', 152.3, -6.2, L),
  ('and how merciless', 'hr6_painpleasure', 180.6, -2.9, L),
  ('that last one', 'hr1_youopened', 326.66, -4.67, L),
  ('put it all', 'hr1_trailer_arrow2', 76.0, -5.7, L)]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}
X[-1]['overlays'].append(['stats', {'name': 'PINHEAD', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'NO MERCY': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'merciless')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# ---- s04 #11 Hellbound 85%: the showcase, Pinhead destroyed by Channard (hr2_tiffvs 1080p, natural speed, cut on the hits) ----
X.append(sec('s04', [(0, 'hr2_tiffvs', 120.85, -1.88),
  ('doctor channard forces', 'hr2_channardpack2', 752.0, -3.6),            # Channard the surgeon
  ('a young patient', 'hr2_tiffany', 41.3, -8.2),                          # Tiffany with the box
  ('to solve the', 'hr2_tiffany', 162.91, -2.84),                          # the box opens into its star
  ('the cenobites spare', 'hr2_tiffany', 262.55, -3.0),                    # Tiffany looks up at them
  ('because the desire', 'hr2_tiffany', 110.35, -1.8), ('his not hers', 'hr2_tiffany', 113.88, -1.36),                    # Pinhead: "it is desire"
  ('then kirsty who', 'hr2_tiffvs', 205.67, -1.8),                           # Kirsty
  ('shows pinhead an', 'hr2_legendary', 50.15, -3.1),                      # the photo
  ('and he remembers', 'hr2_legendary', 93.5, -2.5),                      # Pinhead remembers
  ('a british army', 'hr2_tiffvs', 201.4, -1.7), ('named elliot', 'hr2_tiffvs', 128.9, -1.5),                         # Captain Elliot Spencer's photo
  ("that's when channard", 'hr2_tiffvs', 130.5, -4.3),            # Channard floats in
  ('now a cenobite', 'hr2_tiffvs', 184.2, -2.5),                  # arms spread
  ('pinhead and his', 'hr2_legendary', 147.75, -1.28),                     # Pinhead and the Cenobites face him
  ('turn their chains', 'hr2_tiffvs', 141.77, -0.83), ('on him', 'hr2_tiffvs', 143.6, -0.77),                      # chains fly at Channard
  ('but his tentacles', 'hr2_tiffvs', 150.27, -5.06),                      # the tentacles fan out
  ('right through them', 'hr2_tiffvs', 155.33, -1.27),                     # a tentacle slashes a chain
  ('he cuts the', 'hr2_tiffvs', 156.6, -0.63),                             # the severed chain falls
  ('cenobites down one', 'hr2_tiffvs', 162.3, -3.27),                     # the female Cenobite cut down
  ('by one', 'hr2_tiffvs', 175.07, -1.33),                                 # Chatterer hit
  ('then turns his', 'hr2_tiffvs', 190.23, -3.4),                          # Channard raises his hands, arcs
  ('pinhead himself', 'hr2_tiffvs', 193.93, -1.47),                        # the beams hit Pinhead
  ('that famous face', 'hr2_tiffvs', 195.40, -1.37),                       # his head white-hot
  ('burns away in', 'hr2_tiffvs', 198.60, -1.13),                          # a beam through his head
  ('light', 'hr2_tiffvs', 199.73, -0.43),                             # Pinhead gone
  ('and for a moment', 'hr2_tiffvs', 200.16, -1.11),                       # Elliot Spencer, human, among the chains
  ('spencer again human', 'hr2_tiffvs', 211.83, -2.1),                     # Spencer close-up
  ("until channard's", 'hr2_tiffvs', 148.65, -1.6), ('blade finishes him', 'hr2_tiffvs', 214.15, -1.15),                        # the blade
  ('kirsty and tiffany', 'hr2_escape', 13.9, -1.4, L),                     # Kirsty and Tiffany running
  ('out of hell', 'hr2_escape', 50.1, -2.8, L),                            # silhouettes running into the light
  ('survival rate', 'hr2_escape', 0.0, -2.53, L)], 'kirsty and tiffany'))  # back on the asylum floor, alive
# ---- s05 #10 Revelations 70% (owner's 1080p Blu-ray) ----
X.append(sec('s05', [(0, 'hr9_rev', 3880.0, -1.5), ('with a different', 'hr9_rev', 4068.0, -6.0), ('on a trip', 'hr9_rev', 1520.0, -2.5),
  ('nico solves the', 'hr9_rev', 1866.0, -2.0), ('and gets dragged', 'hr9_rev', 2173.75, -1.7), ('he claws his', 'hr9_rev', 2199.4, -16.0),
  ('by getting his', 'hr9_rev', 3274.5, -14.6), ('then kills steven', 'hr9_rev', 3349.0, -4.9), ('and wears his', 'hr9_rev', 3020.0, -2.5),
  ('back home he', 'hr9_rev', 3651.4, -20.0), ("steven's sister emma", 'hr9_rev', 3736.66, -4.25), ('open the box', 'hr9_rev', 3780.57, -2.42),
  ('so the cenobites', 'hr9_rev', 3806.06, -4.29), ("they don't", 'hr9_rev', 4146.0, -2.5), ("they kill nico's", 'hr9_rev', 3914.08, -1.17),
  ('on the spot', 'hr9_rev', 3922.38, -4.09), ('and pinhead refuses', 'hr9_rev', 3951.7, -3.9), ('as they haul', 'hr9_rev', 4024.78, -4.0),
  ("steven's dying father", 'hr9_rev', 4020.15, -4.63), ('shoots nico dead', 'hr9_rev', 4028.2, -1.8),
  ("take steven's mother", 'hr9_rev', 4112.78, -2.42), ('in his place', 'hr9_rev', 4115.2, -5.5),
  ('only emma the', 'hr9_rev', 4184.98, -2.79, L), ('is left', 'hr9_rev', 4191.27, -13.0, L), ('survival rate', 'hr9_rev', 4204.62, -4.1, L)],
  'only emma the'))
# ---- s06 #9 Hellraiser 1987 55% ----
X.append(sec('s06', [(0, 'hr1_pack4k', 122.9, -2.6), ('frank solves the', 'hr1_pack4k', 10.43, -15.67),
  ('and the cenobites rip', 'hr1_trailer_arrow', 26.55, -1.23), ('with hooked chains', 'hr1_trailer_arrow2', 53.4, -2.81),
  ('when kirsty solves', 'hr1_youopened', 36.04, -14.0), ('she thinks fast', 'hr1_youopened', 333.2, -1.88),
  ('she offers them', 'hr1_youopened', 344.12, -2.14), ('frank who escaped', 'hr1_youopened', 346.26, -4.92),
  ('in exchange for', 'hr1_youopened', 359.5, -2.61), ('they tear frank', 'hr1_jesuswept', 124.25, -1.63), ('all over again', 'hr1_jesuswept', 129.4, -2.1),
  ('then come for', 'hr1_sights', 4.6, -5.1), ('and she only', 'hr1_sights', 9.75, -1.45, L),
  ('by reversing the', 'hr1_dont', 0.0, -2.79, L), ('and sending them', 'hr1_dont', 2.79, -1.92, L), ('back to hell', 'hr1_dont', 6.88, -1.63, L),
  ('survival rate', 'hr1_pack4k', 30.33, -4.24, L)], 'and she only'))
# ---- s07 #8 Hellseeker 45% ----
X.append(sec('s07', [(0, 'hr6_painpleasure', 186.4, -4.0), ('and kirsty is', 'hr6_kirstypack', 4.97, -1.41),
  ('her cheating husband', 'hr6_kirstypack', 19.03, -3.87), ('so he gets', 'hr6_kirstypack', 121.67, -13.5),
  ('but this time', 'hr6_kirstypack', 140.35, -7.5), ('she offers pinhead', 'hr6_kirstypack', 168.75, -4.35),
  ('then she kills', 'hr6_kirstypack', 173.15, -5.25), ('mistresses', 'hr6_weird', 153.75, -4.6), ('then bret the', 'hr6_kirstypack', 191.15, -7.18),
  ('and finally trevor', 'hr6_kirstypack', 198.35, -1.53), ('she walks away', 'hr6_kirstypack', 289.8, -16.0),
  ('survival rate', 'hr6_pain', 204.9, -4.0, L)], 'she walks away'))
# ---- s08 #7 Hellraiser 2022 35% ----
X.append(sec('s08', [(0, 'hr22_bridge', 2.6, -3.6),
  ('where pinhead is', 'hr22_trailer_20th', 97.5, -2.08),
  ('this box has', 'hr22_carousel', 498.0, -16.5),
  ('and each one', 'hr22_carousel', 140.9, -8.6),
  ("riley's brother matt", 'hr22_carousel', 357.85, -1.21),
  ('cuts himself', 'hr22_carousel', 359.06, -0.95),
  ('on it and', 'hr22_carousel', 370.23, -1.42),
  ('vanishes', 'hr22_carousel', 536.2, -3.3),
  ('and her friend nora', 'hr22_trailer_20th', 95.92, -1.52),
  ('is flayed alive', 'hr22_nora', 187.87, -3.56),
  ('riley only gets', 'hr22_bridge', 0.0, -2.5),
  ('by stabbing her', 'hr22_bridge', 33.0, -4.2),
  ('boyfriend', 'hr22_voight', 70.22, -1.48),
  ('as the final', 'hr22_carousel', 171.3, -4.7),
  ('his name is', 'hr22_changed', 4.55, -2.9),
  ('yes another trevor', 'hr22_changed', 36.52, -1.62),
  ("and he'd secretly", 'hr22_voight', 26.0, -5.1),
  ('the millionaire who', 'hr22_voight', 6.45, -6.5),
  ('and when the priest', 'hr22_nora', 145.67, -7.93, L),
  ('bring her brother', 'hr22_carousel', 470.0, -3.5, L),
  ('she says no', 'hr22_bridge', 20.6, -3.2, L),
  ('survival rate', 'hr22_bridge', 27.0, -3.0, L)], 'and when the priest'))
# ---- s09 #6 Bloodline 25% ----
X.append(sec('s09', [(0, 'hr4_space', 0.0, -3.85),
  ('the family of', 'hr4_birth', 184.0, -11.0),
  ('is cursed and', 'hr4_birth', 305.38, -29.0),
  ('this pinhead comes', 'hr4_pathway', 99.5, -4.5),
  ('in nineteen', 'hr4_straighthell', 23.62, -2.46),
  ('he kills the man', 'hr4_straighthell', 27.42, -1.54),
  ('then john merchant', 'hr4_pathway', 104.2, -9.15),
  ('in twenty-one', 'hr4_space', 48.2, -10.8),
  ('he and his cenobites', 'hr4_finalbattle', 123.15, -6.0),
  ('wipe out almost', 'hr4_finalbattle', 68.8, -5.0),
  ('crew of a', 'hr4_finalbattle', 85.5, -1.75),
  ('in the end', 'hr4_another', 272.55, -1.15),
  ('it takes that', 'hr4_another', 262.6, -2.5),
  ('folded into', 'hr4_another', 273.8, -3.0),
  ('to finally destroy', 'hr4_another', 279.3, -2.0, L),
  ('survival rate', 'hr4_chart', 158.8, -4.9, 'flip=1,z=1.35,dx=249')], 'to finally destroy'))
# ---- s02 #5 Hellworld 20% ----
X.append(sec('s02', [(0, 'hr8_welcome', 66.2, -4.1),
  ('five friends go', 'hr8_trailer', 14.68, -1.6),
  ('hellraiser-themed party', 'hr8_jake', 50.0, -2.0),
  ('pinhead takes', 'hr8_welcome', 90.8, -3.5),
  ('mike ends up', 'hr8_welcome', 98.9, -2.4),
  ('and a cop', 'hr8_cop', 31.5, -2.1),
  ('then the twist', 'hr8_welcome', 84.67, -2.8),
  ('the host who', 'hr8_welcome', 87.5, -3.3),
  ('had drugged all', 'hr8_explain', 152.6, -1.2),
  ('five and buried', 'hr8_explain', 213.85, -2.35),
  ('those kills were', 'hr8_jake', 109.7, -3.4),
  ('but allison derrick', 'hr8_explain', 301.6, -4.85),
  ('really do die', 'hr8_explain', 310.25, -4.6),
  ('only chelsea and', 'hr8_explain', 340.2, -4.4),
  ('jake are dug', 'hr8_jake', 38.6, -4.3),
  ('and when the', 'hr8_welcome', 8.2, -6.4, L),
  ('the real pinhead', 'hr8_welcome', 54.0, -3.0, L),
  ('then his cenobites', 'hr8_welcome', 102.8, -1.4, L),
  ('tear him apart', 'hr8_welcome', 104.2, -1.0, L),
  ('survival rate', 'hr8_welcome', 116.5, -3.5, L)], 'and when the'))
# ---- s10 #4 Deader 15% ----
X.append(sec('s10', [(0, 'hr7_returns', 89.2, -4.4),
  ('in bucharest a', 'hr7_real', 20.2, -5.9),
  ('finds a cult', 'hr7_afraid', 146.2, -1.4),
  ('that kills its', 'hr7_afraid', 147.9, -1.1),
  ('and brings them', 'hr7_afraid', 4.55, -3.5),
  ('all because their', 'hr7_returns', 7.59, -1.58),
  ('wants to become', 'hr7_returns', 75.6, -5.6),
  ("he can't open", 'hr7_apt11', 168.03, -2.84),
  ('so he kills', 'hr7_returns', 10.55, -2.4),
  ('to do it', 'hr7_youopened', 1.42, -2.29),
  ('when she does', 'hr7_youopened', 3.71, -1.55),
  ('pinhead slaughters the', 'hr7_returns', 175.6, -1.55),
  ('whole cult then', 'hr7_returns', 166.2, -1.35),
  ('tells her she', 'hr7_youopened', 63.8, -1.9),
  ('and that her', 'hr7_returns', 189.1, -4.0),
  ('rather than be', 'hr7_returns', 148.18, -1.2, L),
  ('she takes her', 'hr7_youopened', 50.66, -2.04, L),
  ('survival rate', 'hr7_returns', 119.1, -2.5, L)], 'rather than be'))
# ---- s03 #3 Judgment 10% ----
X.append(sec('s03', [(0, 'hr10_hell4k', 370.2, -3.1),
  ('here hell has', 'hr10_judge4k', 17.0, -4.3),
  ('called the stygian', 'hr10_scifinow', 9.6, -1.8),
  ('where an auditor', 'hr10_scifinow', 12.0, -2.2),
  ('and a jury', 'hr10_judge4k', 152.15, -3.5),
  ('detective sean secretly', 'hr10_hell4k', 315.7, -2.5),
  ('forces his brother', 'hr10_hell4k', 318.24, -11.8),
  ('then offers them', 'hr10_judge4k', 510.36, -2.62),
  ('pinhead refuses any', 'hr10_judge4k', 518.12, -3.8),
  ('chains rip into', 'hr10_judge4k', 528.3, -1.8),
  ('and drag them', 'hr10_judge4k', 563.92, -2.85),
  ('pinhead has sean', 'hr10_judge4k', 559.16, -1.13),
  ('and even lets', 'hr10_judge4k', 560.33, -3.55),
  ('which finally gets', 'hr10_judge4k', 584.42, -5.3, L),
  ('survival rate', 'hr10_judge4k', 503.06, -2.45, L)], 'which finally gets'))
# ---- s11 #2 Inferno 8% ----
X.append(sec('s11', [(0, 'hr5_box', 266.2, -1.7),
  ('detective joseph', 'hr5_world', 50.9, -20.9),
  ('solves the box', 'hr5_box', 27.1, -4.0),
  ('and spends the', 'hr5_engineer', 116.7, -6.2),
  ('who picks off', 'hr5_torment', 189.8, -1.2),
  ('the people around', 'hr5_torment', 81.15, -4.7),
  ('then his own', 'hr5_child', 97.1, -2.3),
  ('to be pinhead', 'hr5_torment', 444.0, -6.0),
  ('and he learns', 'hr5_torment', 494.4, -14.0),
  ("there's no fight", 'hr5_torment', 548.65, -4.0),
  ('just an eternity', 'hr5_torment', 508.62, -3.55, L),
  ('survival rate', 'hr5_torment', 517.42, -4.8, L)], 'just an eternity'))
# ---- s12 #1 Hell on Earth 5% ----
X.append(sec('s12', [(0, 'hr3_club', 81.25, -3.15),
  ('this pinhead feeds', 'hr3_setfree', 200.02, -1.8),
  ('until he breaks', 'hr3_setfree', 222.58, -2.5),
  ("and once he's", 'hr3_setfree', 248.6, -3.55),
  ('he needs no', 'hr3_iamtheway', 9.6, -3.3),
  ('he massacres an', 'hr3_club', 124.8, -1.9),
  ('entire nightclub', 'hr3_dancefloor', 60.0, -1.2),
  ('and turns some', 'hr3_cenoloose', 76.14, -1.26),
  ('brand new cenobites', 'hr3_cenoloose', 100.5, -3.3),
  ('who then kill', 'hr3_cenoloose', 138.31, -6.0),
  ('only joey with', 'hr3_finalbattle', 301.75, -1.9),
  ('turned into a', 'hr3_finalbattle', 322.22, -0.88),
  ('can send him', 'hr3_finalbattle', 343.0, -3.1),
  ("inferno's pinhead wanted", 'hr5_torment', 465.0, -11.8),
  ('this one wants', 'hr3_club', 72.0, -2.7),
  ("if he's the one", 'hr3_finalbattle', 293.05, -5.25, L),
  ('survival rate', 'hr3_pillar', 224.35, -3.1, L)], "if he's the one"))
# ---- s13 outro ----
X.append(sec('s13', [(0, 'still_posterwall', 0.0, -5.0),
  ('from the one who', 'hr2_legendary', 34.75, -4.6),
  ('to the one with', 'hr3_unstoppable', 85.4, -2.5),
  ('which box would', 'hr1_pack4k', 81.55, -12.8),
  ('and honestly i', 'hr9_rev', 4090.0, -4.0),
  ("we're a small", 'hr22_bridge', 8.0, -3.5),
  ('thanks for watching', 'hr4_pathway', 172.0, -11.0),
  ('keep that box', 'hr2_tiffany', 71.65, -5.6)], pad=2.0,
  extra=[('title', ['WHICH BOX', '!WOULD YOU OPEN?'], 'which box would', 'and honestly i'), ('png', 'tiles/subscribe.png', 'every subscribe', 'thanks for watching'),
         ('title', ['KEEP THAT BOX', '!CLOSED'], 'keep that box', 999)]))
