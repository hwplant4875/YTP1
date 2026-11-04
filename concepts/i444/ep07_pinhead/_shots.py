X = []
# EP07 Pinhead (pipeline as EP06). (word, clip, in, -clean): fit() slows a shot to stay inside its clean span. In-points from verified
# frame strips (agent scans 11/02 + own checks). Miramax clips: logo 0-2.5 s and end cards avoided; 4:3 Hell on Earth clips zoomed to fill.
X.append(sec('s00', [(0, 'hr1_pack4k', 45.7, -5.9), ('he can', 'hr1_pack4k', 108.4, -2.4), ('hook', 'hr2_legendary', 154.65, -0.8),
  ('chains', 'hr2_legendary', 156.5, -0.7), ('peel', 'hr22_carousel', 256.3, -2.6), ('skin', 'hr22_carousel', 261.4, -2.3),
  ('turn you', 'hr3_pillar', 128.0, -7.8), ('or trap', 'hr5_box', 265.7, -2.2), ('head forever', 'hr5_cruelty', 33.5, -13.0),
  ('and he does', 'hr4_pathway', 124.95, -6.5), ('like a priest', 'hr3_iamtheway', 126.55, -1.35), ('reading', 'hr3_iamtheway', 131.0, -1.8),
  ("we're ranking", 'hr1_pack4k', 122.9, -2.6)],
  extra=[('word', 'Pinhead', 0, 'he can'), ('word', 'Hooked chains', 'hook', 'peel'), ('word', 'Peel off your skin', 'peel', 'turn you'),
         ('word', 'One of his Cenobites', 'turn you', 'or trap'), ('word', 'Trapped in your own head', 'or trap', 'and he does'),
         ('word', 'Like a priest reading your sentence', 'like a priest', "we're ranking"),
         ('title', ['EVERY PINHEAD'], "we're ranking", 999)], clip_db=-20))
for ov in X[-1]['overlays']:  # captions flash and cut out: one word 0.9 s max, a phrase 1.5 s max (EP02 rule); the frame-0 caption holds to its cut
    if ov[0] == 'word' and ov[2] > 0: ov[3] = min(ov[3], ov[2] + (0.9 if ' ' not in ov[1] else (2.2 if len(ov[1]) > 25 else 1.5)))
s01_end = vdur('s01') + 0.5
X.append(sec('s01', [(0, 'hr1_pack4k', 62.4, -3.4), ('you just', 'hr1_pack4k', 10.5, -13.9), ("this movie's", 'hr1_pack4k', 81.55, -12.8),
  ('strength', 'hr4_chart', 60.25, -7.4), ('intelligence', 'hr2_legendary', 89.8, -6.1), ('kill count', 'hr7_returns', 75.6, -5.6),
  ('supernatural', 'hr3_pillar', 230.15, -3.9), ('which really', 'hr4_pathway', 152.3, -6.2), ('and that gives', 'hr2_desire', 101.9, -8.9),
  ('your survival', 'hr1_trailer_arrow2', 76.0, -5.7)]))
X[0]['vfade'] = {'out': 0.25}; X[-1]['vfade'] = {'in': 0.25}
X[-1]['overlays'].append(['stats', {'name': 'PINHEAD', 'tile_png': 'tiles/mystery.png', 'stats': {'STRENGTH': 6, 'INTELLIGENCE': 7,
  'KILL COUNT': 5, 'SUPERNATURAL': 8}, 'pct': '??', 'dur': round(s01_end, 3), 't_pct': round(T('s01', 'survival rate') + LEAD, 3),
  'reveal': [round(T('s01', w) + LEAD, 3) for w in ('strength', 'intelligence', 'kill count', 'supernatural')]}, 0.0, 999])
X[-1]['sfx'] = [[0.0, SFX + 'whoosh.wav', SFX_GAIN['whoosh']], [T('s01', 'survival rate') + LEAD, SFX + 'stamp.wav', SFX_GAIN['stamp']]]
# #11 Hellworld 80%
X.append(sec('s02', [(0, 'hr8_welcome', 66.2, -4.1), ('a group', 'hr8_trailer', 14.6, -0.85), ('themed party', 'hr8_trailer', 15.5, -0.75),
  ('and most', 'hr8_jake', 66.2, -5.2), ('set up by', 'hr8_welcome', 8.2, -6.4), ('two of them', 'hr8_cop', 43.4, -4.1),
  ('and when the real', 'hr8_welcome', 116.5, -3.9), ('he takes', 'hr8_jake', 109.7, -3.4), ('survival rate', 'hr8_welcome', 66.2, -4.1)], 'two of them'))
# #10 Judgment 60%
X.append(sec('s03', [(0, 'hr10_hell4k', 370.2, -1.5), ('this time', 'hr10_souls', 27.0, -27.0), ('where an auditor', 'hr10_scifinow', 9.6, -4.2),
  ('and pinhead mostly', 'hr10_judge4k', 523.4, -4.8), ("if you're not", 'hr10_judge4k', 498.6, -4.3), ('and by the end', 'hr10_judge4k', 17.0, -4.3),
  ('survival rate', 'hr10_hell4k', 370.2, -1.5)], "if you're not"))
# #9 Hellbound 55%
X.append(sec('s04', [(0, 'hr2_legendary', 89.8, -6.1), ('pinhead is still', 'hr2_legendary', 53.4, -5.3), ('but this is', 'hr2_legendary', 50.15, -3.1),
  ('and he remembers', 'hr2_legendary', 64.45, -3.3), ('a moment later', 'hr2_legendary', 158.8, -2.6), ('cuts through', 'hr2_legendary', 147.75, -1.5),
  ('in seconds', 'hr2_legendary', 153.95, -0.3), ('and kirsty', 'hr2_legendary', 219.2, -1.0), ('survival rate', 'hr2_desire', 101.9, -8.9)], 'a moment later'))
# #8 Revelations 50% (v1: graphic-free ARC trailer shots; owner may supply a sharper film file)
X.append(sec('s05', [(0, 'hr9_trailer_rt', 72.4, -1.6), ('two friends', 'hr9_trailer_rt', 24.4, -1.5), ('on a trip', 'hr9_trailer_rt', 3.0, -4.5),
  ('one gets', 'hr9_trailer_rt', 38.2, -1.6), ('and pinhead refuses', 'hr9_trailer_rt', 74.2, -1.6), ('but he leaves', 'hr9_trailer_rt', 86.0, -1.6),
  ('and emma', 'hr9_trailer_rt', 46.2, -1.6), ('survival rate', 'hr9_trailer_rt', 72.4, -1.6)], 'but he leaves'))
# #7 Hellraiser 1987 40%
X.append(sec('s06', [(0, 'hr1_pack4k', 122.9, -2.6), ('frank solves', 'hr1_pack4k', 10.5, -13.9), ('and the cenobites', 'hr1_pack4k', 6.5, -3.8),
  ('hook chains', 'hr1_pack4k', 110.85, -1.5), ('so completely', 'hr1_pack4k', 81.55, -12.8), ('kirsty survives', 'hr1_sights', 2.4, -7.2),
  ('by making', 'hr1_pack4k', 30.4, -4.0), ('and then reversing', 'hr1_dont', 0.05, -1.85), ('before they', 'hr1_dont', 6.95, -1.4),
  ('survival rate', 'hr1_pack4k', 45.7, -5.9)], 'kirsty survives'))
# #6 Hellseeker 35%
X.append(sec('s07', [(0, 'hr6_painpleasure', 186.4, -4.0), ('kirsty opens', 'hr6_pain', 204.9, -4.0), ('she offers', 'hr6_painpleasure', 180.6, -2.9),
  ('including', 'hr6_pain', 32.5, -3.0), ('it works', 'hr6_pain', 204.9, -4.0), ('five people', 'hr6_painpleasure', 186.4, -4.0),
  ('survival rate', 'hr6_painpleasure', 180.6, -2.9)], 'it works'))
# #5 Hellraiser 2022, the Priest 30%
X.append(sec('s08', [(0, 'hr22_bridge', 2.6, -3.6), ('where pinhead', 'hr22_trailer_hulu', 97.5, -2.0), ('the box has', 'hr22_carousel', 498.0, -16.5),
  ('every single', 'hr22_carousel', 140.9, -8.6), ("riley's brother", 'hr22_carousel', 256.3, -2.6), ('nora', 'hr22_carousel', 261.4, -2.3),
  ('and trevor', 'hr22_cenofeat', 34.6, -1.2), ('riley and colin', 'hr22_bridge', 0.0, -2.5), ('but only', 'hr22_bridge', 33.0, -4.2),
  ('riley turns', 'hr22_bridge', 23.8, -6.4), ('survival rate', 'hr22_bridge', 2.6, -3.6)], 'riley and colin'))
# #4 Bloodline 25%
X.append(sec('s09', [(0, 'hr4_pathway', 152.3, -6.2), ('pinhead hunts', 'hr4_pathway', 99.5, -4.5), ('kills john', 'hr4_pathway', 96.95, -2.4),
  ('and wipes out', 'hr4_chart', 60.25, -7.4), ('space station', 'hr4_space', 48.2, -10.8), ('in the end', 'hr4_another', 272.55, -1.15),
  ('full of light', 'hr4_another', 273.8, -1.25), ('to finally', 'hr4_another', 279.3, -2.0), ('survival rate', 'hr4_chart', 158.8, -4.9)], 'in the end'))
# #3 Deader 15%
X.append(sec('s10', [(0, 'hr7_returns', 89.2, -4.4), ('a reporter', 'hr7_real', 20.2, -5.9), ('that kills', 'hr7_afraid', 146.2, -2.9),
  ('all because', 'hr7_afraid', 4.55, -3.5), ('when amy', 'hr7_returns', 10.55, -5.4), ('pinhead slaughters', 'hr7_returns', 75.6, -5.6),
  ('and he tells', 'hr7_returns', 189.1, -4.0), ("amy's only", 'hr7_returns', 119.1, -2.5), ('survival rate', 'hr7_returns', 89.2, -4.4)], 'when amy'))
# #2 Inferno 8%
X.append(sec('s11', [(0, 'hr5_box', 265.7, -2.2), ('detective', 'hr5_world', 50.9, -20.9), ('opens the box', 'hr5_box', 27.1, -4.0),
  ('and spends', 'hr5_cruelty', 33.5, -13.0), ('until he learns', 'hr5_child', 97.1, -2.3), ('pinhead the entire', 'hr5_box', 265.7, -2.2),
  ("there's no fight", 'hr5_box', 44.5, -2.9), ('just an eternity', 'hr5_cruelty', 22.0, -1.8), ('survival rate', 'hr5_box', 265.7, -2.2)], 'until he learns'))
# #1 Hell on Earth 5%
X.append(sec('s12', [(0, 'hr3_iamtheway', 131.0, -1.8), ('pinhead breaks', 'hr3_pillar', 128.0, -7.8), ('with no box', 'hr3_pillar', 230.15, -3.9),
  ('massacres', 'hr3_iamtheway', 67.35, -9.2), ('turns his', 'hr3_pillar', 224.35, -3.1), ('only joey', 'hr3_iamtheway', 122.1, -0.85),
  ('turned into', 'hr3_iamtheway', 127.95, -2.9), ('can send', 'hr3_unstoppable', 106.5, -1.6), ("if he's the one", 'hr3_iamtheway', 9.6, -3.3),
  ('survival rate', 'hr3_iamtheway', 126.55, -1.35)], 'only joey'))
X.append(sec('s13', [(0, 'hr1_pack4k', 62.4, -3.4), ('to a demon', 'hr3_pillar', 230.15, -3.9), ('tell me', 'hr1_pack4k', 10.5, -13.9),
  ('and remember', 'hr4_pathway', 172.0, -11.0)], pad=2.5,
  extra=[('title', ['WHICH BOX', '!WOULD YOU OPEN?'], 'tell me', 'and remember'), ('title', ['SOME DOORS', '!STAY CLOSED'], 'and remember', 999)]))
