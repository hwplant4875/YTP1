# 3D 타임랩스 효율·품질 향상 도구 조사 (2026-10-25)

노트북 조건은 GTX 1060 6GB, Blender 5.2, 코드(파이썬)로 굴리는 방식이에요. ★ 표시는 바로 도입을 추천하는 도구예요.

## 1. 애니 그림체 (렉 없이)

| 도구 | 가격 | 효과 | 메모 |
|---|---|---|---|
| ★ Eevee 직접 툰 셰이더: Shader to RGB, 2~3단 컬러램프, 림라이트 | 무료 | 셀 셰이딩, 그림자 단계 | 코드로 모든 재질에 일괄 적용 가능하고 렌더 비용이 거의 0이에요. |
| ★ 외곽선(inverted hull): Solidify + 뒤집힌 노멀 | 무료 | 애니 윤곽선 | 거인, 사람, 건물에 잘 맞아요. Freestyle보다 훨씬 빨라요. |
| Grease Pencil Line Art 모디파이어 | 무료 | 손그림 같은 선 | 큰 장면에서는 느려요. 클로즈업에만 써요. |
| Toon Shader Pack (Superhive, GPL) | 약 1달러 | Eevee용 셀 셰이더 노드 모음 (Blender 4.5~5.2) | 직접 만드는 것의 출발점으로 좋아요. |
| Goo Engine (DillonGoo 블렌더 포크) | Patreon | 애니 전용 렌더 기능 | 블렌더 4.1 기반이라 지금 파이프라인과 버전이 안 맞아요. 비추천이에요. |

## 2. 에셋 생성과 확보

| 도구 | 가격 | 용도 |
|---|---|---|
| ★ Tripo (도입 완료) | 크레딧 | 거인, 소품. 리깅도 돼요. |
| ★ Mixamo | 무료 | 사람형 모델 자동 리깅과 달리기, 쓰러지기, 경례 같은 모션 수천 개. Tripo 거인에도 적용할 수 있어요. |
| Poly Haven | 무료(CC0) | 돌, 흙, 기와 텍스처와 하늘 HDRI |
| BlenderKit | 무료/유료 | 중세 소품, 나무, 건물 부품 |
| Sketchfab (사용 중) | 무료/유료 | AoT 팬 모델 |
| ★ Quaternius / Kenney | 무료(CC0) | 저폴리 사람, 카트, 배, 나무, 건물 팩. 상업적 이용 가능하고 출처 표기도 필요 없어요. |
| Meshy / Rodin | 크레딧 | Tripo 경쟁 도구 |
| Hunyuan3D-2 / TRELLIS | 무료 | 오픈소스지만 VRAM 16GB 이상이 필요해서 1060에서는 안 돌아가요. |

## 3. 지형과 자연

| 도구 | 가격 | 메모 |
|---|---|---|
| ★ Geometry Nodes 스캐터 (직접 작성) | 무료 | 나무 수십만 그루를 인스턴스로 깔아 가볍게 유지해요. 지금 쓰는 방식이에요. |
| A.N.T. Landscape (내장 애드온) | 무료 | 언덕과 능선 지형 생성 |
| Sapling Tree Gen (내장) | 무료 | 나무 모델 몇 종을 만들어 인스턴스로 써요. |
| Geo-Scatter, Botaniq | 유료 | 고품질 식생. 지금 단계에서는 없어도 돼요. |

## 4. 렌더 속도 (효과가 가장 큼)

| 도구 | 가격 | 효과 |
|---|---|---|
| ★ 프레임 보간: RIFE / Flowframes | 무료 | 15fps로 렌더하고 30fps로 보간하면 최종 렌더 시간이 절반이 돼요. 거인이나 카메라처럼 부드러운 움직임에 잘 맞아요. |
| ★ AI 업스케일: Real-ESRGAN (anime 모델) | 무료 | 720p로 렌더하고 1080p로 업스케일하면 시간이 약 2배 줄어요. 애니 그림체에 특히 잘 맞아요. |
| OpenImageDenoise (내장) | 무료 | 샘플 수를 줄여도 깨끗해요. |
| Topaz Video AI | 유료 | 보간과 업스케일 품질이 더 좋지만 비싸요. |
| ★ 클라우드 GPU (RunPod, Vast.ai) | 시간당 약 0.4~0.8달러 | RTX 4090을 빌리면 최종 렌더가 1060보다 10~20배 빨라요. EP 하나에 몇 달러 수준이에요. |
| SheepIt 렌더팜 | 무료 | 대기열과 업로드 제한이 있어요. |
| Kuwahara 필터 (내장 컴포지터) | 무료 | 살짝 손그림 느낌을 내요. 후처리라 가벼워요. |

효과음: 이미 연결된 ElevenLabs로 거인 발소리, 성문 파괴, 입체기동, 대포, 군중 비명을 만들 수 있어요.

## 추천 도입 순서
1. **Eevee 툰 셰이더 + 외곽선:** 무료이고 지금 바로 적용할 수 있어요. 애니 느낌이 가장 크게 올라가요.
2. **Mixamo 모션:** 무료예요. 사람과 거인의 동작이 자연스러워져요.
3. **RIFE 보간 + Real-ESRGAN 업스케일:** 무료예요. 최종 렌더 시간이 약 4분의 1로 줄어요.
4. **Tripo:** 주요 거인과 소품만 만들어요.

출처: [cgchannel Goo Engine](https://www.cgchannel.com/2023/07/check-out-goo-engine-blender-for-anime), [Blender NPR build](https://www.cgchannel.com/2024/12/check-out-blenders-experimental-non-photorealistic-rendering-build/), [Toon shader addons 2026](https://www.strayspark.studio/blog/best-blender-toon-shader-addons-2026), [Toon Shader Pack](https://superhivemarket.com/products/toon-shader-pack-stylized-npr-shading-for-blender-eevee-engine/docs)
