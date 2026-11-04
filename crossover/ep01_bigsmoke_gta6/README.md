# 크로스오버 밈 편집 EP01: 빅 스모크 × GTA 6

다음 세션이 이 작업을 이어받기 위한 기록이다. 이 폴더가 작업 루트다(스크립트는 모두 이 폴더에서 `python3 -I scripts/...`로 실행한다). 영상, 음원 분리 결과, 누끼 같은 큰 파일은 커밋하지 않는다(.gitignore). 아래 순서대로 다시 만든다.

## 상태 (2026-11-04 21:10 KST)
- 스레드 "새 채널 벤치마킹". 사용자가 EP1으로 빅 스모크(GTA SA) × GTA 6를 골랐다. GTA 6 발매일은 2026-11-19다.
- 30초 HD 테스트 컷 v2를 전달했다. 두 파일은 배경음만 다르다.
  - `/mnt/project-files/crossover/EP01_bigsmoke_gta6/BigSmoke_GTA6_test_v2_musicA.mp4` (Keep It Coming, 95 bpm G-funk)
  - `/mnt/project-files/crossover/EP01_bigsmoke_gta6/BigSmoke_GTA6_test_v2_musicB.mp4` (Coastin' stripped, 92 bpm)
- 사용자의 배경음 선택과 피드백을 기다리는 중이다.
- 다음 순서: 피드백 반영 → 전체 편 약 100초(16:9) → 쇼츠 3~4개(9:16, 안전 영역) → 업로드 전 미리보기 → 사용자 OK 후 업로드. 올릴 채널은 아직 정하지 않았다(추천: PEEK./FP).

## 원칙
- 대사는 두 작품의 실제 대사만 쓴다. 내레이션, AI 음성, AI 영상은 쓰지 않는다.
- GTA SA 소스 왼쪽 위의 GTA-Series.com 워터마크는 지우지 않는다. 빅 스모크가 그 상자와 겹치지 않는 테이크만 고르고, 누끼에서 그 상자 영역만 0으로 만든다.
- 쇼츠 안에서 같은 클립을 다시 쓰지 않는다. 무음은 1.5초를 넘기지 않는다.
- 배경음은 로열티 프리(Splice)만 쓰고, 스테레오를 유지하며, 조용하게 깐다(최종 약 -27 LUFS).

## 소스
공식 타임라인 = HD 파일 시간 + offset (`hd/offsets.json`). EDL과 누끼 작업(jobs/)의 시간은 공식 타임라인 기준이다. 음원 분리 결과(`aud/sephd`)는 HD 파일 시간 기준이라 오디오 표에서 offset을 뺀다.

| 키 | HD 파일 | 내용 |
|---|---|---|
| E_a, E_b, E_c, E_d, E_g | E_*.mkv | GTA 6 공식 긴 영상(서버 360p 기준본 tJbzMqJGH4k)을 1440p 재업로드 dL962fBSDZI에서 잘라낸 구간 |
| BG_a, BG_b | BG_*.mkv | GTA SA 빅 스모크 컷신(기준본 OpTizzox2Qo). 720p, 워터마크 있음 |
| EL_a, EL_b | EL_*.mkv | GTA SA End of the Line(기준본 H5lj23EUR9U) |
| T1 | QdBZY2fkU-0.mkv | GTA 6 트레일러 1 |
| T2 | VQRLujxTm3c.mkv | GTA 6 트레일러 2 |
| L | rz1B4B2yBZY.mkv | GTA 6 제이슨·루시아 영상("I got in some trouble in the army…") |
| DT | E1aTlYlfzRk.mkv | GTA SA 드라이브스루(빅 스모크 주문) |
| TR | cF3GK_sfPVM.mkv | "All we had to do was follow the damn train, CJ!" |

- HD 파일 14개는 노트북 `E:\YTP2\Crossover\EP01 Big Smoke GTA6\1_work\seg`에 같은 이름으로 있다(전체 다운로드는 `src`). 노트북에서는 공식 Extended Look이 연령 제한이라 재업로드 dL962fBSDZI를 받았다.
- 서버 쿠키는 노트북으로 옮기지 않는다. 쿠키 파일(ck.txt)은 커밋하지 않는다.

## 새 컨테이너에서 다시 만들기
```bash
pip install onnxruntime opencv-python-headless numpy faster-whisper
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && pip install demucs
mkdir -p models && curl -sSL -o models/rvm_mobilenetv3_fp32.onnx \
  https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx
```
1. HD 파일: 노트북 seg 폴더의 14개 파일을 `hd/`로 가져온다(device_stage_files).
2. 음원 분리(CPU라 오래 걸린다. 테스트 컷에는 BGb, T2, DT 보컬과 Ea 배경음만 필요하다):
   ```bash
   mkdir -p aud/hd && for k in T2:VQRLujxTm3c.mkv T1:QdBZY2fkU-0.mkv L:rz1B4B2yBZY.mkv Ec:E_c.mkv Ea:E_a.mkv Eb:E_b.mkv DT:E1aTlYlfzRk.mkv BGb:BG_b.mkv BGa:BG_a.mkv ELa:EL_a.mkv ELb:EL_b.mkv TR:cF3GK_sfPVM.mkv Ed:E_d.mkv Eg:E_g.mkv; do n=${k%%:*}; f=${k#*:}; ffmpeg -loglevel error -y -i hd/$f -vn -ac 2 -ar 44100 -c:a pcm_s16le aud/hd/$n.wav; done
   (cd aud/hd && python3 -m demucs --two-stems=vocals -n htdemucs -o ../sephd BGb.wav T2.wav DT.wav Ea.wav)
   ```
3. 누끼: `for j in jobs/M_A.json jobs/M_bat.json jobs/W_B1.json jobs/W_D.json jobs/W_F.json jobs/W_P.json; do NT=4 python3 -I scripts/matte.py $j; done` (프레임당 약 0.15초). 결과는 `mattes/<이름>/f_*.png`(RGBA)와 meta.json이다. 예전 meta는 `mattes_meta/`에 있다.
   - 점검: `python3 -I scripts/mcheck.py mattes/W_F` (프레임별로 가장자리·워터마크 상자에 닿는지), `python3 -I scripts/mruns.py mattes/W_F 1270` (깨끗한 구간), `python3 -I scripts/msheet.py sheet.jpg mattes/W_F` (자홍색 배경 시트).
4. 효과음·배경음: `/mnt/project-files/crossover/EP01_bigsmoke_gta6/work/sfx/`를 `sfx/`로 복사한다. 없으면 아래 Splice UUID로 다시 받는다.
5. 렌더: `python3 -I scripts/render_segs.py edl_test.py out_test_v2.mp4` (샷마다 `segs/`에 캐시하고 바뀐 샷만 다시 렌더한다. 4코어 CPU로 전체 약 5분. 샷 시작 시간은 `out_test_v2.mp4.marks.json`에 쓴다.)
6. 믹스: `BGM=sfx/bgm_keep_it_coming.wav python3 -I scripts/mix.py audio_test.py out_v2_mixA.wav` (B는 `BGM=sfx/bgm_coastin_stripped.wav`).
7. 합치기: `bash scripts/mux.sh out_test_v2.mp4 out_v2_mixA.wav out_A.mp4`.
8. 점검: `python3 -I scripts/qa_frames.py out_A.mp4 out_test_v2.mp4.marks.json qa/` (샷마다 처음·중간·끝 프레임 시트). 대사 확인은 `python3 -I scripts/tseg.py <wav> <시작> <끝> ["힌트"]`(faster-whisper small.en).

## 깨끗한 누끼 구간 (BG_b, 공식 시간)
전체 폭 ROI + 시드 영역 방식이다. CJ는 빅 스모크와 닿지 않는 한 떨어져 나간다. ROI 가장자리나 워터마크 상자에 닿는 프레임은 쓰지 않는다.

| 이름 | 쓸 수 있는 구간 | 테스트 컷에서 쓴 곳 |
|---|---|---|
| M_bat | 392.0–396.6 (배트가 원본 왼쪽 끝에 닿아서 ox ≤ 0으로 배치, 0–6프레임은 워터마크 때문에 제외) | C2 392.9(0.75배속), C4 394.75 |
| M_A | 405.5–408.17 (ROI 0–790) | S4 405.6, S15 407.55 |
| W_B1 | 410.7–412.37, 412.6–413.17 | S6 410.7, S13 412.6 |
| W_D | 430.4–431.53 | S8 430.4 |
| W_F | 418.57–421.0 | S17 418.6, S3 420.05 |
| W_P | 402.47–403.63, 404.93–405.6 | S10 402.47 |
| W_E | 419.3–421.0, 421.77–422.27 | 아직 안 씀 |
| W_C, W_B2 | 0.35초 조각, 418.57–419.3뿐 | 안 씀 |

전체 편에는 테이크가 더 필요하다. DT, EL, TR에서 새 누끼를 딴다.

## 룩 (테스트 컷 v2)
- 배경: GTA 6 정지 화면을 약 2배로 확대하고 흐림 4~5(피사계 심도처럼), 천천히 줌.
- 색 맞춤: Lab 매칭(L 0.40, a 0.20, b 0.20), 채도 1.06, 라이트 랩 0.35, 그레인 3.2, 전경 샤픈 0.55, erode 1, soft 0.9.
- 배치: `edl_test.py`의 `place()`. 샷 전체에서 머리 윗선이 가장 높은 프레임을 기준으로 위 여백 110px, 모자 폭 205px, 최대 배율 1.85. ROI 바닥은 화면 아래로 살짝 내린다.
- 편의점 배경은 E_b 706.4 오른쪽(cx 0.76, 루시아가 안 보이게), 집 배경은 E_a 274.3(cx 0.75)이다.

## 오디오 (테스트 컷 v2)
- 대사 클립마다 LUFS를 맞춘다(-15~-16). 효과음은 -24~-25(총 장전 소리 -16). 앰비언스는 E_a 배경음 분리본에 6 kHz 저역 통과를 걸어 -34로 콜드 오픈 전체에 깐다.
- 배경음은 믹스 전 -29.5(최종 약 -27)에 highshelf 3 kHz -4 dB를 걸고, 스테레오를 유지한다.
- 마지막에 2패스 loudnorm으로 -14 LUFS, TP -1.5에 맞춘다.
- 360p 자막은 틀릴 수 있다. "CJ?"는 없는 대사였고 실제 대사는 "Oh... my dog, what's up?"이다. HD 보컬로 다시 확인한다.

## Splice 자산
| 파일 | 원본 이름 | asset UUID |
|---|---|---|
| bgm_keep_it_coming.wav | RKU_RWCT_95_songstarter_keep_it_coming_alt_Gmin.wav | dff6c3ae-9c93-47f8-879a-080c4f0ff794 |
| bgm_coastin_stripped.wav | RKU_RWCT_92_songstarter_coastin_stripped_alt_G#min.wav | bd122215-dfdc-42a0-b4b5-5e96980340eb |
| bat_whoosh.wav | ESM_Game_Baseball_Bat_1_Swing_Sport_Cricket_Tennis_Whoosh_Synth_Swoosh.wav | 00086df0-9f20-4c5f-b41f-d9fed2909207 |
| door_wood.wav | BRS_Door_Wood_Cheap_Handle_Mvs_1.wav | 17383d17-c621-42de-ba34-f3e0a43b8aa0 |
| register.wav | BRS_Cash_Register_Drawer_Open_1.wav | 32a99573-505e-4c21-b639-eb88699e357d |
| gun_cock.wav | SAC_E_gun_cock.wav | 7309bf06-68a4-46b1-bc88-110315b665e0 |

## 알려진 한계
- 주문 대사는 드라이브스루 장면 소리라서 입 모양은 대략만 맞는다.
- GTA SA 원본이 720p라 빅 스모크가 배경보다 조금 부드럽다(샤픈으로 보정).
- 트레일러의 "Hands above your head"는 실제로는 "...up above your head"일 수 있다(어느 쪽이든 실제 대사다).

## 작업 중 주의
- `pkill -f`에 현재 명령줄과 겹치는 패턴을 쓰면 자기 셸이 같이 죽는다.
- 백그라운드로 돌린 `&&` 체인에서는 mux가 끝난 뒤에 qa를 돌린다.
- 원본 샷 경계 근처에서 자르면 옆 장면 프레임이 1~2개 섞인다. 160x90 흑백 프레임 차이로 컷 위치를 찾아서 피한다.
