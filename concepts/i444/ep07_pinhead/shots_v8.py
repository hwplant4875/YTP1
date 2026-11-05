# EP07 v8 shot plan (owner-approved script_v8.md, 11/05), read by build_edl_v8.py. A shot is (phrase, clip, in_s, -clean_s[, opts]).
# Every in-point is a frame-checked span from the v7 work (beats_v7.md, shots_v7.py, QA rounds 1-4) unless marked NEW.
# Rules: every "This Pinhead ..." line shows that film's Pinhead; comparison lines stay on the current film; L = subject left of the stat card.
L = 'z=1.35,dx=249'
# ---- s00 cold open: frame 0 = 1987 Pinhead full frame; "This Pinhead will" once; every chunk its own caption and cut ----
X.append(sec('s00', [(0, 'hr1_pack4k', 34.57, -11.0),                        # 1987 Pinhead, hospital blinds (cover frame)
  ('tear straight', 'hr1_jesuswept', 117.49, -0.67),                       # hook in Frank's shirt
  ('through your flesh', 'hr1_jesuswept', 122.75, -1.5),                   # chains rip his chest
  ('with hooked', 'hr1_jesuswept', 127.21, -2.13),                         # Frank's face pulled by the hooks
  ('peel your', 'hr9_rev', 2190.3, -2.8),                                  # Revelations: a Cenobite hand peels Nico's flayed face
  ('while', 'hr9_rev', 2183.7, -3.3),                                      # Revelations: Nico alive, screaming in the hooks
  ('turn you', 'hr3_cenoloose', 145.5, -2.1),                              # Pistonhead
  ('one of his', 'hr3_cenoloose', 105.9, -2.8),                            # Barbie
  ('cenobites', 'hr3_cenoloose', 178.04, -5.0),                            # Camerahead
  ('or trap', 'hr5_torment', 420.85, -1.8),                                # chains whip around Thorne
  ('inside', 'hr5_torment', 425.1, -3.0),                                  # Thorne hung in his own Hell
  ('forever', 'hr5_torment', 450.33, -3.7),                                # Thorne held there
  ('and he does', 'hr2_tiffvs', 125.5, -3.3),                              # Hellbound Pinhead
  ('all of it', 'hr3_iamtheway', 126.55, -1.35),                           # Hell on Earth Pinhead
  ('calmly', 'hr1_pack4k', 45.6, -11.5),                                   # the calm 1987 stare
  ("we're ranking", 'still_posterwall', 0.0, -5.0)],                       # the 11 posters
  extra=[('word', w, a, b) for w, a, b in [
    ('This Pinhead will', 0, 'tear straight'), ('Tear straight', 'tear straight', 'through your flesh'),
    ('Through your flesh', 'through your flesh', 'with hooked'), ('With hooked chains', 'with hooked', 'peel your'),
    ('Peel your skin off', 'peel your', 'while'), ("While you're still alive", 'while', 'turn you'),
    ('Turn you into', 'turn you', 'one of his'), ('One of his', 'one of his', 'cenobites'), ('Cenobites', 'cenobites', 'or trap'),
    ('Or trap you', 'or trap', 'inside'), ('Inside your own head', 'inside', 'forever'), ('Forever', 'forever', 'and he does'),
    ('And he does', 'and he does', 'all of it'), ('All of it', 'all of it', 'calmly'), ('Calmly', 'calmly', "we're ranking"),
    ("We're ranking", "we're ranking", 'every pinhead'), ('Every Pinhead', 'every pinhead', 'by your chance'),
    ('By your chance', 'by your chance', 'of surviving'), ('Of surviving him', 'of surviving', 999)]], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out (one word 0.9 s, a phrase 1.6 s max); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else 1.6))
# ---- s01 rules (stat card from frame 0, subjects left of it) ----
s01_end = vdur('s01') + 0.05
X.append(sec('s01', [(0, 'hr1_pack4k', 62.4, -3.4),
  ('you just', 'hr2_tiffany', 49.59, -9.9),                                # hands on the box
  ("that movie's", 'hr1_pack4k', 108.4, -2.4, L),                          # 1987 Pinhead
  ('and every pinhead', 'hr22_bridge', 8.0, -3.5, L),                      # the Priest
  ('some play by', 'hr2_tiffvs', 188.97, -1.26, L),                        # Hellbound Pinhead
  ('some take your', 'hr22_bridge', 23.8, -3.0, L),                        # the Priest offering
  ("and one doesn't", 'hr3_finalbattle', 304.0, -5.6, L),                  # Hell on Earth Pinhead
  ('so we score', 'hr4_pathway', 125.0, -6.4, L),
  ('intelligence', 'hr4_pathway', 152.3, -6.2, L),
  ('and how much', 'hr6_painpleasure', 180.6, -2.9, L),
  ('which decides', 'hr1_youopened', 326.66, -4.67, L),                    # Kirsty bargaining
  ('put it all', 'hr1_trailer_arrow2', 76.0, -5.7, L)]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}
X[-1]['overlays'].append(['stats', {'name': 'PINHEAD', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'NO MERCY': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'mercy')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# ---- s04 #11 Hellbound 85%: the showcase, Pinhead destroyed by the doctor (hr2_tiffvs 1080p, natural speed, cut on the hits) ----
X.append(sec('s04', [(0, 'hr2_tiffvs', 120.85, -1.88),                    # Hellbound Pinhead
  ('of all the', 'hr2_legendary', 53.4, -5.3),                             # Pinhead close-up
  ('this is the one', 'hr2_legendary', 34.75, -4.6),                       # Pinhead
  ('because he plays', 'hr2_legendary', 140.0, -1.2),                      # Pinhead close-up
  ('when a doctor', 'hr2_channardpack2', 752.0, -3.6),                     # human Dr Channard, surgeon
  ('young patient', 'hr2_tiffany', 41.3, -8.2),                            # Tiffany
  ('to solve the', 'hr2_tiffany', 162.91, -2.84),                          # the box opens into its star
  ('the cenobites spare', 'hr2_tiffany', 262.55, -3.0),                    # Tiffany looks up at them
  ('because the desire', 'hr2_tiffany', 110.35, -1.8),                     # Channard: "It's what I've always wanted"
  ('his not hers', 'hr2_tiffany', 113.88, -1.36),                          # Channard: "I have to know"
  ('this pinhead still', 'hr2_legendary', 89.8, -3.6),                     # Pinhead close-up
  ('one look at', 'hr2_legendary', 50.15, -3.1),                           # the photo
  ('and he remembers', 'hr2_legendary', 93.5, -2.5),                       # "I... remember"
  ('a british army', 'hr2_tiffvs', 201.4, -1.7),                           # Captain Elliot Spencer's photo
  ('named elliot', 'hr2_tiffvs', 128.9, -1.5),                             # the photo again
  ('and he can', 'hr2_legendary', 147.75, -1.28),                          # Pinhead and his crew face the doctor
  ('that same doctor', 'hr2_tiffvs', 130.5, -4.3),                         # Cenobite Channard arrives: "Ah, good. A fight."
  ('now a cenobite', 'hr2_tiffvs', 184.2, -2.5),                           # Channard close-up
  ('cuts down', 'hr2_tiffvs', 150.27, -5.06),                              # the tentacles fan out
  ('whole crew', 'hr2_tiffvs', 162.3, -3.27),                              # a Cenobite cut down
  ('then burns', 'hr2_tiffvs', 193.93, -1.47),                             # the beams hit Pinhead
  ('famous face', 'hr2_tiffvs', 195.40, -1.37),                            # his head white-hot
  ('away in', 'hr2_tiffvs', 198.60, -1.13),                                # a beam through his head
  ('light', 'hr2_tiffvs', 199.73, -0.43),                                  # Pinhead gone
  ('and for a', 'hr2_tiffvs', 200.16, -1.11),                              # Elliot Spencer's profile as the glow fades
  ('elliot spencer again', 'hr2_tiffvs', 211.83, -2.1),                    # Spencer close-up, human
  ('until the', 'hr2_tiffvs', 148.65, -1.6),                               # Channard close-up
  ('blade finishes', 'hr2_tiffvs', 214.15, -1.15, L),                      # the blade
  ('survival rate', 'hr2_escape', 0.0, -2.53, L)], 'blade finishes'))      # Kirsty and Tiffany, alive
# ---- s05 #10 Revelations 70% (owner's 1080p Blu-ray) ----
X.append(sec('s05', [(0, 'hr9_rev', 3880.0, -1.5),
  ('with a different', 'hr9_rev', 4068.0, -6.0),                           # Revelations Pinhead
  ('this pinhead is', 'hr9_rev', 3942.19, -1.67),                          # Pinhead
  ('far stricter', 'hr9_rev', 4146.0, -2.5),                               # Pinhead
  ("he won't take", 'hr9_rev', 4072.0, -2.0),                              # NEW span: Pinhead close-up
  ("he'll kill you", 'hr9_rev', 3927.97, -4.84),                           # Pinhead over Kate
  ('and he never', 'hr9_rev', 4120.70, -3.22),                             # Sarah with the Cenobites
  ('when nico tries', 'hr9_rev', 3651.4, -20.0),                           # Nico with the shotgun, Emma
  ('his own girlfriend', 'hr9_rev', 3947.12, -2.04),                       # Nico: "I called you to trade her for me"
  ('pinhead refuses', 'hr9_rev', 3951.7, -3.9),                            # "Trade? No."
  ("when nico's mother", 'hr9_rev', 3914.08, -1.17),                       # Kate, hooks in her throat
  ('the cenobites kill', 'hr9_rev', 3922.38, -4.09),                       # Kate chained
  ('and when nico', 'hr9_rev', 4020.15, -4.63),                            # Ross aims
  ('shot dead', 'hr9_rev', 4028.2, -1.8),                                  # the hit
  ('as they drag', 'hr9_rev', 4033.74, -7.96),                             # Nico in the chains, blood in his mouth
  ("they take emma's", 'hr9_rev', 4112.78, -2.42),                         # Sarah hooked
  ('in his place', 'hr9_rev', 4115.2, -5.5),                               # Sarah taken
  ('but emma', 'hr9_rev', 4184.98, -2.79),                                 # Emma close-up
  ('opened the box', 'hr9_rev', 3780.57, -2.42),                           # Emma's hands open the box
  ('is the only', 'hr9_rev', 4191.27, -13.0),                              # Emma alone
  ('keep quiet', 'hr9_rev', 4151.9, -3.96, L),                             # Emma close-up
  ('want nothing', 'hr9_rev', 4204.62, -4.1, L),                           # Emma with the box
  ('survival rate', 'hr9_rev', 4198.0, -2.2, L)], 'keep quiet'))
# ---- s06 #9 Hellraiser 1987 55% ----
X.append(sec('s06', [(0, 'hr1_pack4k', 122.9, -2.6),
  ('unlike the last', 'hr1_pack4k', 30.33, -4.24),                         # 1987 Pinhead
  ('this pinhead will', 'hr1_youopened', 346.26, -2.1),                    # Pinhead answers Kirsty
  ("and that's the", 'hr1_youopened', 362.11, -2.42),                      # the Cenobites
  ('when frank opens', 'hr1_pack4k', 10.43, -15.67),                       # Frank's hands on the box
  ('hooked chains tear', 'hr1_trailer_arrow', 26.55, -1.23),               # Frank screams as the hooks hit
  ('tear him apart', 'hr1_trailer_arrow2', 53.4, -2.81),                   # Frank wrenched up by the hooks
  ('when kirsty opens', 'hr1_youopened', 36.04, -14.0),                    # Kirsty with the box in the hospital
  ('she offers them', 'hr1_youopened', 344.12, -2.14),                     # "He escaped you."
  ('who escaped', 'hr1_youopened', 333.2, -1.88),
  ('in exchange for', 'hr1_youopened', 359.5, -2.61),                      # "please do this"
  ('pinhead agrees', 'hr1_youopened', 349.0, -2.1),                        # Pinhead
  ('tears frank', 'hr1_jesuswept', 124.25, -1.63),                         # Frank torn open by the chains
  ('all over again', 'hr1_jesuswept', 129.4, -2.1),                        # Kirsty watches
  ('and then comes', 'hr1_sights', 4.6, -5.1),                             # Pinhead looms behind Kirsty
  ('with this one', 'hr1_pack4k', 57.17, -1.8),                            # Kirsty
  ('and to live', 'hr1_sights', 9.75, -1.45),                              # Kirsty alone
  ('solve the box', 'hr1_dont_sdr', 0.0, -2.79),                           # she twists the box shut
  ('and send him', 'hr1_dont_sdr', 2.79, -1.92, L),                        # Pinhead
  ('before he can', 'hr1_dont_sdr', 6.88, -1.63, L),                       # the box closes
  ('survival rate', 'hr1_pack4k', 38.0, -6.0, L)], 'and send him'))
# ---- s07 #8 Hellseeker 45% ----
X.append(sec('s07', [(0, 'hr6_painpleasure', 186.4, -4.0),
  ('this pinhead keeps', 'hr6_pain', 198.5, -2.5),                         # Hellseeker Pinhead
  ('as long as', 'hr6_painpleasure', 175.3, -2.5),                         # Pinhead with Trevor
  ("when kirsty's", 'hr6_kirstypack', 19.03, -3.87),                       # Kirsty and Trevor in the car
  ('gets her to', 'hr6_kirstypack', 121.67, -13.5),                        # Kirsty works the box
  ('she saves herself', 'hr6_kirstypack', 140.35, -7.5),                   # "How did you find me?"
  ('five souls for', 'hr6_kirstypack', 168.75, -4.35),                     # "I will bring you five souls"
  ('so she kills', 'hr6_kirstypack', 173.15, -5.25),                       # "You'll get your five."
  ("trevor's mistresses", 'hr6_weird', 153.75, -4.6),                      # a mistress with Trevor
  ('then bret', 'hr6_kirstypack', 191.15, -7.18),                          # "I made a better offer"
  ('and finally trevor', 'hr6_kirstypack', 198.35, -1.53),                 # the gun on Trevor
  ('who spends', 'hr6_pain', 32.5, -3.0),                                  # Trevor, lost
  ('most people', 'hr6_kirstypack', 289.8, -16.0),                         # Kirsty walks away
  ("and that's why", 'hr6_pain', 204.9, -4.0, L),                          # Pinhead
  ('survival rate', 'hr6_painpleasure', 184.0, -1.9, L)], "and that's why"))
# ---- s08 #7 Hellraiser 2022 35% ----
X.append(sec('s08', [(0, 'hr22_bridge', 2.6, -3.6),
  ('where pinhead is', 'hr22_trailer_20th', 97.5, -2.08),                  # the Priest
  ('the last one', 'hr22_nora', 118.9, -3.7),                              # the Priest (logo cropped by the zoom)
  ("but the priest's", 'hr22_carousel', 498.0, -16.5),                     # the box
  ('and every victim', 'hr22_carousel', 140.9, -8.6),
  ("riley's brother", 'hr22_carousel', 357.85, -1.21),                     # Matt
  ('cuts himself', 'hr22_carousel', 359.06, -0.95),                        # his hands take the box
  ('on it and', 'hr22_carousel', 370.23, -1.42),                           # his bloody palm
  ('vanishes', 'hr22_carousel', 536.2, -3.3),                              # the empty bathroom
  ('and her friend', 'hr22_trailer_20th', 95.92, -1.52),                   # Nora hung by hooks
  ('nora is skinned', 'hr22_nora', 187.87, -3.56),                         # Nora (cut before the worst frame)
  ('riley only', 'hr22_bridge', 0.0, -2.5),                                # Riley
  ('stabbing her', 'hr22_bridge', 33.0, -4.2),                             # Riley with the box's blade
  ('boyfriend', 'hr22_voight', 70.22, -1.48),                              # Voight over the wounded Trevor
  ('yes another', 'hr22_changed', 4.55, -2.9),                             # Trevor
  ("who'd secretly", 'hr22_voight', 26.0, -5.1),                           # Voight
  ("the box's owner", 'hr22_voight', 6.45, -6.5),                          # Voight with the blade
  ('as the final', 'hr22_carousel', 171.3, -4.7),                          # the box's blade
  ('and when the priest', 'hr22_nora', 145.67, -4.0),                      # the Priest
  ('bring her brother', 'hr22_carousel', 470.0, -3.5),                     # Matt, bloodied
  ('she has to', 'hr22_bridge', 20.6, -3.2),                               # Riley: "No."
  ('to walk away', 'hr22_bridge', 27.0, -3.0, L),                          # the Priest
  ('then turn down', 'hr22_trailer_hulu', 97.5, -2.0, L),                  # the Priest
  ('survival rate', 'hr22_nora', 150.0, -3.5, L)], 'to walk away'))
# ---- s09 #6 Bloodline 25% ----
X.append(sec('s09', [(0, 'hr4_space', 0.0, -3.85),
  ("running won't", 'hr4_pathway', 99.5, -4.5),                            # Bloodline Pinhead
  ("because he doesn't", 'hr4_finalbattle', 85.5, -1.75),                    # a man screams between the Twins
  ('he comes for', 'hr4_haunted', 64.0, -2.0),                             # NEW: John Merchant with his wife Bobbi (1996)
  ('the family of', 'hr4_birth', 184.0, -11.0),                            # the Duc and LeMarchand (1796)
  ('is cursed', 'hr4_birth', 305.38, -29.0),                               # Jacques bloody in the chains
  ('so in nineteen', 'hr4_straighthell', 23.62, -2.46),                    # Sharpe chained (1996)
  ('this pinhead kills', 'hr4_straighthell', 59.0, -8.96),                 # Pinhead emerges
  ('john merchant', 'hr4_haunted', 70.0, -1.6),                            # NEW: John Merchant close-up
  ('in new york', 'hr4_pathway', 104.2, -9.15),                            # John facing Pinhead
  ('and in twenty-one', 'hr4_space', 48.2, -10.8),                         # the station
  ('when one of', 'hr4_another', 262.6, -2.5),                             # Dr Paul Merchant
  ('he wipes out', 'hr4_finalbattle', 123.15, -6.0),                       # Pinhead on the station
  ('the entire crew', 'hr4_finalbattle', 68.8, -5.0),                      # the Twins
  ('it takes that', 'hr4_another', 272.55, -1.15),                         # the light
  ('folded into', 'hr4_another', 273.77, -1.38),                           # the box of light bursts
  ('full of light', 'hr4_another', 279.25, -1.0),                          # Pinhead caught in the light
  ('to finally destroy', 'hr4_another', 280.25, -1.35, L),                 # Pinhead destroyed
  ('survival rate', 'hr4_chart', 158.8, -4.9, 'flip=1,z=1.35,dx=249')], 'to finally destroy'))
# ---- s02 #5 Hellworld 20% ----
X.append(sec('s02', [(0, 'hr8_welcome', 66.2, -4.1),
  ('this pinhead barely', 'hr8_cop', 43.4, -4.1),                          # Hellworld Pinhead in the woods
  ('a grieving father', 'hr8_explain', 177.6, -3.5),                       # the Host
  ('drugs five', 'hr8_explain', 152.6, -1.2),                              # the Host
  ('and buries', 'hr8_explain', 213.85, -2.35),                            # the graves
  ('in their nightmare', 'hr8_trailer', 14.68, -1.6),                      # the party
  ("they're picked", 'hr8_jake', 0.4, -6.7),                               # a Cenobite lurking in the doorway
  ('with pinhead even', 'hr8_jake', 109.7, -3.4),                          # Pinhead appears
  ('spike through', 'hr8_cop', 31.5, -2.1),                                # the cop and the spike
  ('the fear is', 'hr8_explain', 162.75, -5.5),                            # NEW span: Chelsea screaming in her grave
  ('allison derrick', 'hr8_explain', 301.6, -4.85),                        # in the coffins
  ('die in their', 'hr8_explain', 310.25, -4.6),                           # a dead face
  ('and only chelsea', 'hr8_explain', 340.2, -4.4),                        # Chelsea alive in her grave
  ('jake survive', 'hr8_jake', 38.6, -4.3),                                # Jake
  ('then the father', 'hr8_welcome', 8.2, -6.4),                           # the Host with the real box
  ('the real pinhead', 'hr8_welcome', 54.0, -3.0),                         # Pinhead
  ('and his cenobites', 'hr8_welcome', 102.8, -1.4),                       # the blade swings
  ('tear him apart', 'hr8_welcome', 104.2, -1.0),                          # the Host hit
  ('on the spot', 'hr8_welcome', 109.3, -1.2),                             # the Host bleeding
  ('no chase', 'hr8_welcome', 116.5, -3.5, L),                             # three Cenobites
  ('survival rate', 'hr8_welcome', 85.0, -2.5, L)], 'no chase'))           # Pinhead stare
# ---- s10 #4 Deader 15% ----
X.append(sec('s10', [(0, 'hr7_returns', 89.2, -4.4),
  ('this pinhead promises', 'hr7_returns', 189.1, -4.0),                   # Deader Pinhead
  ('when a reporter', 'hr7_real', 20.2, -5.9),                             # Amy
  ('opens his box', 'hr7_youopened', 3.71, -1.55),                         # the opened box
  ('he kills off', 'hr7_returns', 175.6, -1.55),                           # Winter, hooks in his face
  ('cult of people', 'hr7_returns', 166.2, -1.35),                         # Winter's face torn
  ('died once', 'hr7_returns', 142.5, -1.6),                               # Winter crucified
  ('then tells her', 'hr7_youopened', 63.8, -1.9),                         # Pinhead
  ('and that her', 'hr7_youopened', 5.26, -4.62),                          # Pinhead at the window
  ('rather than', 'hr7_returns', 148.18, -1.2, L),                         # Amy
  ('amy takes', 'hr7_youopened', 76.0, -2.0, L),                           # Amy close-up in the final scene (never the act)
  ('survival rate', 'hr7_returns', 119.1, -2.5, L)], 'rather than'))
# ---- s03 #3 Judgment 10% ----
X.append(sec('s03', [(0, 'hr10_hell4k', 370.2, -3.1),
  ("this pinhead doesn't", 'hr10_judge4k', 503.06, -2.45),                   # Judgment Pinhead close-up
  ('because hell has', 'hr10_judge4k', 17.0, -4.3),                        # the Inquisition office
  ('an auditor', 'hr10_scifinow', 9.6, -1.8),                              # the Auditor
  ('and a jury', 'hr10_judge4k', 152.15, -3.5),                            # the Assessor (face only)
  ('a detective', 'hr10_hell4k', 259.45, -2.1),                            # Sean's confession
  ('forces his', 'hr10_hell4k', 318.24, -11.8),                            # hands forced onto the box
  ('and offers them', 'hr10_judge4k', 510.36, -2.62),                      # "Them for me. Adulterers."
  ('but pinhead refuses', 'hr10_judge4k', 518.12, -3.8),                   # "no bargaining to be done"
  ('chains rip', 'hr10_judge4k', 528.3, -1.8),                             # David and Alison among the chains
  ('and drag them', 'hr10_judge4k', 563.92, -2.85),                        # Alison terrified
  ('and the jury', 'hr10_judge4k', 560.33, -3.55),                         # Sean, guilty
  ('in this hell', 'hr10_judge4k', 584.42, -5.3, L),                       # the Surgeon and the Butcher
  ('survival rate', 'hr10_judge4k', 523.4, -2.2, L)], 'in this hell'))
# ---- s11 #2 Inferno 8% ----
X.append(sec('s11', [(0, 'hr5_box', 266.2, -1.7),
  ('this is the smartest', 'hr5_welcome', 0.0, -5.1),                      # Inferno Pinhead close-up
  ('because you never', 'hr5_cruelty', 22.0, -1.8),                        # the creature of his hell
  ('detective joseph', 'hr5_world', 50.9, -20.9),                          # Thorne
  ('solves the box', 'hr5_box', 27.1, -4.0),
  ('and spends the', 'hr5_engineer', 116.7, -6.2),
  ('who picks off', 'hr5_torment', 189.8, -1.2),
  ('the people around', 'hr5_torment', 81.15, -4.7),
  ('until his own', 'hr5_child', 97.1, -2.3),
  ('turns out to', 'hr5_torment', 444.0, -6.0),                            # Pinhead beside the child
  ('and he learns', 'hr5_torment', 494.4, -14.0),                          # "the hell you have created for yourself"
  ("there's no fight", 'hr5_torment', 548.65, -4.0),
  ('just pain', 'hr5_torment', 508.62, -3.55, L),
  ('survival rate', 'hr5_torment', 517.42, -4.8, L)], 'just pain'))
# ---- s12 #1 Hell on Earth 5% ----
X.append(sec('s12', [(0, 'hr3_club', 81.25, -3.15),
  ('every other pinhead', 'hr3_finalbattle', 314.0, -3.7),                 # Hell on Earth Pinhead
  ('but this one', 'hr3_iamtheway', 131.0, -1.8),                          # Pinhead
  ('he feeds on', 'hr3_setfree', 200.02, -1.8),                            # Pinhead screaming in the Pillar
  ('until he breaks', 'hr3_setfree', 222.58, -2.5),                        # the Pillar bursts
  ("and once he's", 'hr3_setfree', 248.6, -3.55),                          # Pinhead free
  ('he needs no', 'hr3_iamtheway', 9.6, -3.3),
  ('he slaughters', 'hr3_club', 124.8, -1.9),                              # the DJ
  ('nightclub', 'hr3_dancefloor', 60.0, -1.2),
  ('and turns some', 'hr3_cenoloose', 76.14, -1.26),                       # Pistonhead
  ('brand new', 'hr3_cenoloose', 100.5, -3.3),                             # Barbie
  ('who then kill', 'hr3_cenoloose', 138.31, -6.0),                        # the new Cenobites at the police cars
  ("inferno's pinhead", 'hr3_pillar', 230.15, -3.9),                       # this film's Pinhead (comparison stays here)
  ('this one wants', 'hr3_club', 72.0, -2.7),                              # Pinhead in the club
  ("if he's the", 'hr3_finalbattle', 293.05, -5.25),                       # Pinhead in the room
  ('no deal will', 'hr3_finalbattle', 299.9, -1.8, L),
  ('survival rate', 'hr3_pillar', 224.35, -3.1, L)], 'no deal will'))
# ---- s13 outro ----
X.append(sec('s13', [(0, 'still_posterwall', 0.0, -5.0),                  # callback to the cold open
  ('from the one who', 'hr2_tiffvs', 203.13, -2.54),                       # Elliot Spencer
  ('to the one with', 'hr3_unstoppable', 85.4, -2.5),                      # Hell on Earth Pinhead
  ('which box would', 'hr1_pack4k', 81.55, -12.8),
  ('and honestly i', 'hr9_rev', 4090.0, -4.0),
  ("we're a small", 'hr6_pain', 201.0, -3.8),
  ('thanks for watching', 'hr4_pathway', 172.0, -11.0),
  ('keep that box', 'hr2_tiffany', 71.65, -5.6)], pad=2.0,
  extra=[('title', ['WHICH BOX', '!WOULD YOU OPEN?'], 'which box would', 'and honestly i'), ('png', 'tiles/subscribe.png', 'every subscribe', 'thanks for watching'),
         ('title', ['KEEP THAT BOX', '!CLOSED'], 'keep that box', 999)]))
