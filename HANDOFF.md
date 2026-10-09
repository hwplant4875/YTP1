# 인수인계: 독일 채널 (YT_REFRESH_TOKEN_CC, 구 "기발한 회사들")

이 문서가 다음 세션의 유일한 기억이다. 작업을 마칠 때마다 갱신해서 커밋한다.

## 1. 채널
- 채널: @기발한회사들 (환경 변수 YT_REFRESH_TOKEN_CC). 2026-10-08 기준 구독자 3명, 쇼츠 9개(기업 기술 컨셉, 중앙값 25회). 기존 컨셉은 폐기했다. 기존 쇼츠 9개는 비공개로 돌리기를 권장한다(삭제는 하지 않는다).
- 새 컨셉: "한국인에게 독일". 독일 문화, 역사, 밈, 축제, 팁. 이름 후보는 "독일 한 스푼"(추천), "오늘의 독일", "독일인 특".
- 목표: 2027-01-31 전에 YPP(1,000명 + 롱폼 4,000시간 또는 쇼츠 1,000만 회/90일) 달성. 2027-02-01부터는 신규 기준이 8,000시간 또는 2,000만 회로 오른다(유튜브 공식 발표).
- 전략: 쇼츠로 구독자를 모으고(하루 1편), 롱폼(8분 이상, 주 2편)으로 시청 시간을 쌓는다. 수익화 심사 전에는 다른 크리에이터 영상 번역을 올리지 않는다. 허락을 받았어도 "재사용 콘텐츠"로 거절될 수 있기 때문이다. 영상은 전부 오리지널로 만든다.

## 2. 절대 규칙
- 남의 영상은 허락 없이 쓰지 않는다. 쓸 수 있는 소스는 퍼블릭 도메인(미국 정부, Universal Newsreel), CC 라이선스(Wikimedia, 출처 표기), Pexels/Pixabay, 그리고 직접 만든 3D다.
- 팩트는 출처가 있는 것만 쓴다. 출처가 없는 유명한 이야기는 빼거나 "~라고 알려져 있다"로 쓴다.
- 영상 안에 색 들어간 직선 같은 기본 그래픽은 쓰지 않는다(사용자 지시).
- 음성은 필재(Typecast voice_id tc_68257f68bc6e3c161ab5078d), 1.3배속, 문장 사이 빈틈 없이.
- 폰트: Pretendard(본문, 라벨, 연도), Noto Serif KR Black(제목, 썸네일). 모두 OFL.

## 3. 환경
- 환경 변수: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN_CC(2026-10-08에 만료 확인, 재발급 필요), TYPECAST_API_KEY, ELEVENLABS_API_KEY(Creator 요금제: 효과음, 음악, Scribe), PEXELS_API_KEY, PIXABAY_API_KEY.
- YouTube OAuth 앱 "Shorts Uploader1": 테스트 모드라 토큰이 7일마다 만료됐다. 프로덕션으로 전환한 뒤 토큰을 재발급해야 한다(OAuth Playground 사용, 범위: youtube, youtube.force-ssl, yt-analytics.readonly). 동의 화면 링크가 예전 youngmen3.github.io를 가리키고 있으면, 이 저장소의 docs/를 GitHub Pages(main, /docs)로 띄운 주소로 바꾼다.
- 드라이브 "효과음 ALL" 폴더에는 .lnk 바로가기만 있다. 실제 음원 업로드가 필요하다. "Reference Videos1" 폴더에는 neo의 "How the Berlin Wall Worked"(64MB)가 있다.
- 도구 설치: `pip install rapidocr_onnxruntime opencv-python-headless pillow fonttools yt-dlp`, `cd germany_shorts/longform && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install`. Chromium은 /opt/pw-browsers에 있다.
- Wikimedia 원본 파일은 429로 막힌다. 1920px 썸네일 주소로 받는다.

## 4. 도구 (germany_shorts/)
- explainer.py: 쇼츠 제작기. 대본 JSON을 받아 필재 음성, Pexels 세로 영상, 한국어 자막, 상단 제목, 효과음, 앰비언스를 넣고 -14 LUFS로 맞춘다. 파일럿은 specs/xmas_mug.json(크리스마스 마켓 컵).
- subswap.py: 허락받은 영상 전용. 박힌 자막을 OCR로 찾아 inpaint와 블러로 지우고, 한국어 자막을 같은 자리에 넣는다.
- longform/render.mjs: Three.js 장면을 헤드리스 Chromium으로 렌더한다. 1080p 기준 프레임당 약 0.7초. 사용법: `node render.mjs scenes/x.js out.mp4 --dur 8 --shot cab --t0 0`.
- longform/scenes/: ghost_station(샷: platform, guard, cab, border, thumb, poster), cross_section(샷: reveal, pass, thumb). 룩은 무채색에 호박색 빛 하나, 안개.
- longform/assemble.py: 롱폼 조립기. 대본 JSON을 받아 TTS(무음 정리), 3D, 사진 켄번스, 기록 영상, 텍스트(YEAR/LABEL/TITLE/QUOTE/CREDIT), 효과음, 덕킹 음악, 그레인, 비네트를 처리하고 SRT와 timeline.json을 만든다. 캐시는 LONGFORM_CACHE.
- PLAN.md: 시장 조사와 아이디어 뱅크.

## 5. 에피소드
- 롱폼 1호 "베를린의 유령역" (longform/episodes/01_ghost_stations): 대본(make_script.py에서 script.json 생성), 리서치(research_ghost.md), 썸네일, 업로드 정보. 길이 7:54이고, 마지막 hold를 9초에서 16초로 늘려 8:01로 맞출 예정이다. 에셋(뉴스릴, Bundesarchiv 사진, 음악)은 git에 넣지 않았다. 다시 받는 방법은 research_ghost.md와 upload_meta.md에 있다.
- 다음 롱폼 후보: 터널 29(NBC가 촬영비를 댄 땅굴 탈출), 베를린 공수와 사탕 폭격기, 샤보프스키의 말실수.
- 쇼츠 파일럿: 크리스마스 마켓 컵(완성). 11월 중순부터 크리스마스 시리즈를 올린다.

## 6. 레퍼런스
- neo(@neoexplains): 3D 지도와 모델, 기록 사진, 2인칭 몰입 인트로, 35초쯤 제목 공개, 실존 인물 장면, 해부식 설명, 다음 이야기 예고. 썸네일은 땅속 단면 + 빛나는 물체 + 1~3단어.
- 한국 시장: 허락받은 독일 번역 채널은 없다. "~하는 이유", "절대 하면 안 되는", "~특" 훅이 강하다. 제목은 20자 이하이고, 제목에 해시태그나 국기는 넣지 않는다.
