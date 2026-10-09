# Fast German (CC 채널, 구 "기발한 회사들")

영어로 독일어를 가르치는 얼굴 없는 채널. 슬로건: "German in seconds, not hours." 기획서: `/mnt/project-files/plans/cc-german/plan.md`.

## 고정 규칙
- 목소리: ElevenLabs **Carola - Sharp and Clear** (`K75lPKuh15SyVhQC1LrE`), 모델 eleven_multilingual_v2. 2026-10-09 사용자 선택.
- 성별 색: der 파랑, die 빨강, das 초록. 모든 영상 동일 (`lib/common.py` GENDER).
- 그림: Microsoft Fluent Emoji flat (MIT), 이름 목록 `assets/icon_names.txt`. 폰트: Fredoka (OFL).
- 강의 언어: 영어.

## 구조
- `lib/common.py`: TTS(타임스탬프 포함, 캐시), 효과음, 아이콘. 캐시는 `/mnt/project-files/fast_german/cache` (다음 세션도 재사용, 재생성 비용 없음).
- `lib/short.py`: 쇼츠 렌더러 (1080x1920). `python3 lib/short.py specs/shorts/01_handschuh.json out/01.mp4`
- `lib/longform.py`: 슬라이드형 롱폼 렌더러 (1920x1080).
- `lib/upload.py`: `upload_plan.json`대로 예약 업로드, 결과는 `uploads.json`. 이미 올린 파일은 건너뜀.
- `specs/make_shorts.py`: 쇼츠 02~13 대본. `specs/build_sleep.py`, `build_crash.py`, `build_kitchen.py`: 롱폼 3개. `specs/thumbs.py`: 썸네일. `specs/upload_plan.py`: 제목·설명·일정.
- 의존성: `pip install cairosvg`, ffmpeg.
