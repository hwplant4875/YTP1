# 기발한 회사들 → 독일 채널 제작 도구

## subswap.py: 원본 자막 지우고 한국어 자막 올리기
허락받은 영상에만 사용한다.

```
pip install rapidocr_onnxruntime opencv-python-headless pillow
python3 subswap.py detect in.mp4 subs.json        # 원본 자막 위치·시간·문장 추출 (OCR, 8초 영상 약 40초)
#   subs.json의 각 segment "ko" 칸에 한국어 자막을 채운다. 줄바꿈은 \n, 강조는 *단어* (노란색)
python3 subswap.py render in.mp4 subs.json out.mp4   # 지우기 + 한국어 자막 (8초 영상 약 1분)
```

동작
- detect: RapidOCR로 2~3프레임마다 글자를 읽고, 같은 줄의 단어 박스를 한 줄로 합치고, 같은 문장이 이어지는 구간을 segment로 묶는다. 화면 위 12%와 아래 10%(유튜브 UI 자리)는 무시(--y-min, --y-max).
- render: 프레임마다 원본 자막 줄 박스 안의 글자 획을 찾아 inpaint로 먼저 지우고, 그 위를 둥근 모서리 + 가장자리 페더 마스크로 가우시안 블러. 그래서 블러 뒤로 원문 글자가 비쳐 보이지 않는다. 박스는 원본 자막 줄에 딱 맞게(여백 --pad 10px) 잡히고, 검정 박스는 쓰지 않는다.
- 한국어 자막: libass, Pretendard Black, 흰 글자 + 진한 테두리 + 반투명 그림자, 원본 자막과 같은 중심 위치, 원본 줄 높이의 1.25배 이상 크기(화면 폭 90% 넘으면 자동 축소), 등장 시 살짝 튀는 팝 애니메이션.
- 옵션: --blur 18, --pad 10, --radius 18, --feather 6, --font BlackHanSans-Regular.ttf, --accent FFD400, --scale 1.0

폰트 (fonts/): Pretendard(OFL), Black Han Sans(OFL). 둘 다 상업 이용 무료.
