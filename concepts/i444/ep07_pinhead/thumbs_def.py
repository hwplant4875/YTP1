# EP07 extra thumbnails D/E/F (owner 11/05: three more, keep A/B/C). Reuses thumbs.py's panel code without re-rendering A/B/C;
# all nine faces are new sources (none in A/B/C or each other). usage: python thumbs_def.py [clips_dir] [out_dir] [posters_dir]
import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thumbs.py'), encoding='utf-8').read()
exec(src[:src.index('# owner 11/04: every face centred')])
FACE, EYE = 150, 215
def F(clip, t, cx, cy, em, pct, col, bright=1.15): return P(clip, t, cx, cy, em, pct, col, bright, face_px=FACE, eye_y=EYE)
three([F('hr2_legendary', 66.0, 720, 470, 315, '85%', GREEN, 1.8),             # Hellbound #11, close-up (Shout HD clip)
       F('hr4_straighthell', 66.0, 875, 215, 100, '25%', YEL, 1.35),            # Bloodline #6, warehouse
       F('hr3_unstoppable', 86.0, 1010, 425, 190, '5%', RED, 1.3)], 'pinhead_thumb_d.jpg')   # Hell on Earth #1, Boiler Room chains
three([F('poster:rev_4070.png', 0, 1090, 435, 200, '70%', GREEN, 1.05),        # Revelations #10, Blu-ray frame
       F('hr22_cenofeat', 39.0, 940, 460, 165, '35%', YEL, 1.2),                # 2022 #7, the Priest
       F('hr7_returns', 92.0, 1160, 285, 150, '15%', RED, 1.6)], 'pinhead_thumb_e.jpg')     # Deader #4
three([F('hr1_sights', 3.0, 1040, 228, 117, '55%', GREEN, 1.4),                # Hellraiser 1987 #9
       F('hr8_welcome', 64.0, 1010, 350, 195, '20%', YEL, 1.7),                # Hellworld #5
       F('hr5_torment', 519.0, 840, 375, 235, '8%', RED, 1.0)], 'pinhead_thumb_f.jpg')       # Inferno #2
