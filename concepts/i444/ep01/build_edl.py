# builds edl_full.json: preview sections (intro, rules, #12) + #11..#1 + outro
import json
P = json.load(open('edl_preview.json'))
def m(s): # "m:ss" or seconds -> seconds
    if isinstance(s, str): a, b = s.split(':'); return int(a) * 60 + float(b)
    return s
def sec(voice, shots, rank=None, odds=None, instr=None, t_odds=None, t_instr=None, extra=(), pad=0.7):
    S = {'voice': voice, 'pad': pad, 'clip_audio_db': -99, 'shots': [[t, n, m(i)] for t, n, i in shots], 'overlays': []}
    if rank: S['overlays'].append(['rank', rank, 0.0, 2.9])
    if odds is not None: S['overlays'].append(['odds', odds, t_odds, t_instr - 0.08])
    if instr: S['overlays'].append(['instr', instr, t_instr, 99])
    S['overlays'] += [list(e) for e in extra]
    return S
X = []
X.append(sec('s03', [(0,'h20_laurie_vs_michael_final_fight_hd','0:15'),(3.32,'h20_trailer','0:33'),(6.0,'h20_trailer','0:36'),(8.0,'h20_trailer','1:00'),
  (10.0,'h20_laurie_vs_michael_final_fight_hd','0:41'),(11.28,'h20_laurie_vs_michael_final_fight_hd','3:15'),(13.0,'h20_laurie_vs_michael_final_fight_hd','3:46'),
  (14.6,'h20_final_confrontation','0:38'),(16.76,'h20_final_confrontation','0:16'),(18.2,'h20_final_confrontation','1:52'),(19.88,'h20_final_confrontation','1:19'),
  (23.32,'h20_final_confrontation','1:36'),(26.0,'h20_final_confrontation','1:06'),(28.8,'h20_final_confrontation','1:44'),(31.36,'h20_trailer','1:27')],
  [11,'Halloween H20',1998], 33, 'Do not hide. Hunt him first.', 28.8, 31.36))
X.append(sec('s04', [(0,'h5_trailer','0:03'),(2.8,'h5_trailer','0:06'),(5.0,'h5_trailer','0:30'),(7.28,'h5_trailer','1:12'),(9.0,'h5_trailer','1:21'),
  (10.88,'h5_trailer','0:33'),(13.0,'h5_trailer','1:06'),(15.5,'h5_trailer','1:00'),(18.28,'h5_extended_ending_hd','1:33'),(20.96,'h5_extended_ending_hd','1:51'),
  (22.24,'h5_extended_ending_hd','2:06'),(24.56,'h5_extended_ending_hd','0:30'),(27.36,'h5_trailer','0:18')],
  [10,'Halloween 5',1989], 29, 'Bait him. Then net him.', 24.56, 27.36))
X.append(sec('s05', [(0,'resurrection_busta_fight_hd','1:09'),(3.04,'resurrection_trailer_hd','0:06'),(5.0,'resurrection_trailer_hd','0:09'),(7.0,'resurrection_trailer_hd','0:39'),
  (8.96,'resurrection_busta_fight_hd','0:57'),(10.5,'resurrection_busta_fight_hd','2:09'),(11.28,'resurrection_trailer_hd','1:12'),(13.6,'resurrection_busta_fight_hd','3:24'),
  (16.0,'resurrection_busta_fight_hd','3:06'),(18.8,'resurrection_trailer_hd','1:06'),(20.48,'resurrection_ending','0:40'),(21.56,'resurrection_ending','0:58'),
  (22.56,'resurrection_ending','1:04'),(24.08,'resurrection_ending','1:06'),(26.64,'resurrection_ending','0:46')],
  [9,'Halloween Resurrection',2002], 22, 'Never trust a body bag.', 24.08, 26.64))
X.append(sec('s06', [(0,'rz2_2009_trailer','1:03'),(3.6,'rz2_2009_trailer','0:21'),(6.0,'rz2_2009_trailer','0:51'),(8.5,'rz2_2009_trailer','1:06'),(11.36,'rz2_2009_trailer','2:03'),
  (12.72,'rz2_2009_trailer','0:30'),(14.5,'rz2_2009_trailer','2:21'),(16.0,'rz2_2009_trailer','1:30'),(17.28,'rz2_2009_trailer','0:12'),(19.0,'rz2_2009_trailer','0:24'),
  (21.84,'rz2_2009_trailer','1:48'),(24.8,'rz2_2009_trailer','0:42'),(27.44,'rz2_2009_trailer','1:03')],
  [8,"Rob Zombie's Halloween II",2009], 18, 'Call the police early. Bring many.', 24.8, 27.44))
X.append(sec('s07', [(0,'1978_every_scene',548.8),(2.4,'1978_every_scene',30),(4.96,'1978_every_scene',112),(7.88,'1978_every_scene',129),(10.08,'1978_every_scene',509),
  (12.56,'1978_every_scene',467.5),(15.2,'1978_closet_attack_hd','0:18'),(17.84,'1978_closet_attack_hd','2:57'),(19.76,'1978_closet_attack_hd','3:12'),
  (21.88,'1978_closet_attack_hd','3:27'),(24.35,'1978_closet_attack_hd','3:36'),(26.12,'1978_closet_attack_hd','3:39'),(28.0,'1978_closet_attack_hd','2:48'),(30.72,'1978_every_scene',591)],
  [7,'Halloween',1978], 15, 'When he falls, do not look away.', 28.0, 30.72))
X.append(sec('s08', [(0,'kills_survives_fire','6:16'),(3.0,'2018_killing_spree','2:09')], pad=0.5,
  extra=[('title', ['SUBSCRIBE', '!TO SURVIVE'], 6.16, 8.9)]))
X.append(sec('s09', [(0,'rz_2007_trailer','0:54'),(3.36,'rz_2007_trailer','0:42'),(6.0,'rz_2007_trailer','1:00'),(8.0,'rz_2007_trailer','1:21'),(10.0,'rz_2007_trailer','1:39'),
  (12.24,'rz_2007_trailer','1:12'),(14.44,'rz_2007_trailer','1:27'),(16.5,'rz_2007_trailer','1:30'),(18.2,'rz_2007_trailer','1:33'),(19.48,'rz_2007_trailer','0:06'),
  (21.76,'rz_2007_trailer','1:24'),(24.4,'rz_2007_trailer','0:51')],
  [6,"Rob Zombie's Halloween",2007], 11, 'Do not let him get his hands on you.', 21.76, 24.4))
X.append(sec('s10', [(0,'2018_killing_spree','2:09'),(3.36,'2018_killing_spree','0:33'),(6.88,'2018_killing_spree','1:39'),(8.56,'2018_killing_spree','2:15'),(10.5,'2018_killing_spree','1:21'),
  (12.16,'2018_hit_and_run_hd','0:42'),(13.0,'2018_hit_and_run_hd','1:21'),(13.6,'2018_hit_and_run_hd','1:24'),(14.88,'2018_laurie_shoots_fingers_hd','1:39'),
  (16.0,'2018_laurie_shoots_fingers_hd','1:42'),(17.04,'2018_burned_alive','3:15'),(19.0,'2018_burned_alive','3:21'),(21.0,'2018_burned_alive','3:39'),(22.88,'2018_burned_alive','3:45'),
  (23.92,'kills_survives_fire','7:07'),(26.8,'2018_laurie_shoots_fingers_hd','2:15'),(29.2,'2018_burned_alive','3:48')],
  [5,'Halloween',2018], 8, 'Fire is not enough. Plan for after.', 26.8, 29.2))
X.append(sec('s11', [(0,'h2_1981_ending','0:42'),(3.96,'1978_every_scene',586),(6.4,'h2_1981_why_wont_he_die','1:46'),(9.0,'h2_1981_why_wont_he_die','0:16'),(11.52,'h2_1981_why_wont_he_die','0:26'),
  (13.52,'h2_1981_ending','0:57'),(14.5,'h2_1981_ending','1:03'),(15.6,'h2_1981_ending','1:12'),(17.0,'h2_1981_ending','2:06'),(19.04,'h2_1981_ending','1:33'),(20.5,'h2_1981_ending','2:27'),
  (21.68,'h2_1981_ending','2:47'),(23.0,'h2_1981_ending','3:18'),(26.0,'h2_1981_ending','3:36'),(28.08,'h2_1981_ending','3:24'),(30.64,'h2_1981_ending','5:18')],
  [4,'Halloween II',1981], 6, 'If he cannot see you, stay silent.', 28.08, 30.64))
X.append(sec('s12', [(0,'curse_tommy_defeats_michael_hd','0:39'),(3.36,'curse_trailer_hd','0:03'),(6.08,'curse_trailer_hd','0:15'),(7.12,'curse_trailer_hd','0:24'),(9.36,'curse_trailer_hd','0:36'),
  (11.92,'curse_trailer_hd','0:45'),(14.08,'curse_tommy_defeats_michael_hd','0:12'),(16.56,'curse_tommy_defeats_michael_hd','1:21'),(18.72,'curse_tommy_defeats_michael_hd','1:30'),
  (20.0,'curse_tommy_defeats_michael_hd','2:03'),(23.12,'curse_tommy_defeats_michael_hd','2:12'),(25.84,'curse_tommy_defeats_michael_hd','1:09'),(28.24,'curse_tommy_defeats_michael_hd','3:03')],
  [3,'The Curse of Michael Myers',1995], 4, 'You cannot kill a curse. Leave town.', 25.84, 28.24))
X.append(sec('s13', [(0,'h4_trailer','1:00'),(2.64,'h4_trailer','1:03'),(5.0,'h4_trailer','1:09'),(7.2,'h4_final_scene_hd','0:27'),(9.04,'h4_trailer','0:57'),(12.0,'h4_final_scene_hd','3:18'),
  (14.16,'h4_final_scene_hd','0:30'),(15.5,'h4_final_scene_hd','1:51'),(16.88,'h4_final_scene_hd','3:45'),(18.5,'h4_final_scene_hd','3:51'),(21.84,'h4_final_scene_hd','4:00'),
  (23.0,'h4_final_scene_hd','4:09'),(24.56,'h4_death_scene',14.0),(26.72,'h4_final_scene_hd','4:24'),(29.44,'h4_final_scene_hd','3:30'),(31.92,'h4_final_scene_hd','1:24')],
  [2,'Halloween 4',1988], 2, 'Do not get in the truck.', 29.44, 31.92))
X.append(sec('s14', [(0,'kills_firefighters','1:48'),(2.8,'kills_survives_fire','4:56'),(6.16,'kills_firefighters','1:15'),(8.88,'kills_firefighters','1:24'),(10.76,'kills_firefighters','1:42'),
  (12.5,'kills_firefighters','0:39'),(14.08,'kills_firefighters','1:51'),(16.0,'kills_crowd_end','0:24'),(18.16,'kills_crowd_end','1:28'),(21.16,'kills_crowd_end','2:20'),
  (22.5,'kills_crowd_end','2:32'),(24.0,'kills_crowd_end','3:08'),(25.12,'kills_crowd_end','3:20'),(26.48,'kills_crowd_end','4:28'),(28.36,'kills_crowd_end','4:48'),
  (30.04,'kills_crowd_end','4:36'),(31.84,'kills_crowd_end','5:24'),(33.92,'kills_crowd_end','7:16'),(36.44,'kills_crowd_end','5:32')],
  [1,'Halloween Kills',2021], 0.5, 'If you hear the theme, you already lost.', 33.92, 36.44))
X.append(sec('s15', [(0,'kills_survives_fire','7:08'),(1.68,'1978_every_scene',548.8),(4.16,'h20_final_confrontation','1:19'),(6.32,'2018_killing_spree','2:09'),(8.6,'BLACK',0)], pad=1.5,
  extra=[('title', ['YOUR RANKING?'], 4.16, 8.5), ('title', ['INSTRUCTION', '!444'], 8.7, 14.3)]))
P['sections'] = P['sections'][:3] + X
P['zoom'].update({'2018_hit_and_run_hd': 1.12, '2018_burned_alive': 1.12, 'kills_firefighters': 1.12, 'h20_final_confrontation': 1.12})
json.dump(P, open('edl_full.json', 'w'), indent=1)
print(len(P['sections']), 'sections')
