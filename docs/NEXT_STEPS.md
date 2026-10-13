# 다음 제작 단계와 작업 인계

최종 갱신: 2026-10-13.

## 채널 정체성

시대와 세계를 자유롭게 여행하며, 도착한 세계의 소리를 우리 일상의 배경음악으로 담는다. 채널 소개 원문은 `README.md`에 기록했다. 주인공 Eunoh는 여러 시대와 세계에 등장한다.

## 현재 상태
- [x] 원본 `direction1_front_v1.png`에서 1회 생성 후 원본을 86.1244% Lanczos 축소 합성한 `runs/euno/drafts/style_2026-10-13/front_16x9_v6.png` 제작 (1920×1080). v5는 어깨·구도 좌표만 참고. 얼굴·기존 머리카락·목·칼라 원본 복원, 화면 오른쪽 점·두 구슬 피어싱 확인. 원본에 없는 정수리 확장부와 26px 연결부는 생성 픽셀이므로 머리카락 전체 원본 보존 조건에는 예외가 있음. 프롬프트·처리 기록·재현 스크립트 저장, 사용자 검토 대기.
- [x] 사용자 요청에 따라 내장 image_gen으로 여성 체형의 좁고 둥근 어깨 수정본 `runs/euno/drafts/style_2026-10-13/front_16x9_v4.png` 제작 (1920×1080). 생성 결과 크기 조정 후 원본 얼굴·머리카락 픽셀을 유지해 합성. 정확한 프롬프트와 처리 방식은 같은 이름의 `_prompt.txt`, `_processing.txt`에 기록. v1/v2/v3 유지, 사용자 검토 대기.
- [x] `front_16x9_v1.png`의 양쪽 어깨 수직 잘림 수정: `runs/euno/drafts/style_2026-10-13/front_16x9_v3.png` (1920×1080). 내장 이미지 편집 결과의 어깨를 원본에 합성해 얼굴·머리카락 원본 픽셀 보존. 정확한 프롬프트와 크기 조정·합성 방식은 같은 이름의 `_prompt.txt`, `_processing.txt`에 기록. 화면 오른쪽 눈썹 두 구슬 피어싱·눈 아래 점 확인.
- [x] 화풍 탐색 시안 5장 제작 (Codex 내장 이미지 생성 도구): `runs/euno/drafts/style_2026-10-13/`. 어깨 위 컬러 선화 2장. 함께 만든 빈티지 시안 3장과 빈티지 참고 이미지 2장은 사용자 요청으로 삭제했다(2026-10-13).
- [x] 사용자가 정면 시안 `direction1_front_v1.png`를 채널 화풍 기준으로 지정: `references/local/channel_style/channel_style_front_bust_20261013.png`로 복사(원본 유지). 기준 내용은 `AGENTS.md`와 `config/style.json`에 기록.
- [x] 같은 기준의 16:9 가로 시안 2장 제작 및 크기·좌우 특징 확인: `runs/euno/drafts/style_2026-10-13/front_16x9_v1.png`, `front_16x9_v2.png` (각 1920×1080). v1은 원본 전체 축소와 좌우 흰 패딩, v2는 내장 이미지 생성 도구로 가로 재생성 후 크기 조정·흰 패딩. 각 `_prompt.txt`에 정확한 프롬프트와 처리 방식 기록.
- [x] 16:9 가로 시안 사용자 검토 및 선택: 사용자가 `front_16x9_v6.png`를 16:9 기준으로 지정(2026-10-13). `references/local/channel_style/channel_style_front_bust_16x9_20261013.png`로 복사(원본 유지).
- [x] 화면 오른쪽 기둥에 가볍게 기대고 고개를 오른쪽으로 돌린 자세 수정본 제작: `runs/euno/worlds/steampunk/standing_goggles_20261012_v5.png` (내장 이미지 생성 도구, 인물 오른쪽 얼굴 노출·반대편 특징을 보이는 볼로 옮기지 않음).
- [x] 사용자 지정 얼굴 `eunoh_base2.jpg`를 참고하여 스팀펑크 장면 재제작: `runs/euno/worlds/steampunk/standing_goggles_20261012_v4.png` (내장 이미지 생성 도구, 얼굴 방향·화면 오른쪽 피어싱과 점 확인).
 
- [x] 스팀펑크 기대 선 자세와 얼굴 좌우 특징 수정본 제작: `runs/euno/worlds/steampunk/standing_goggles_20261012_v3.png` (내장 이미지 생성 도구, 화면 오른쪽 눈썹 피어싱·오른쪽 눈 아래 점, 원본 유지).

- [x] 사용자 확정 Eunoh 좌우 특징을 `AGENTS.md`에 기록: 화면 기준 오른쪽 눈썹 피어싱·오른쪽 눈 아래 점 (인물 기준 왼쪽). 과거 기록보다 이 규칙을 우선한다.

- [x] 고글을 머리에 올리고 기둥에 기대 선 스팀펑크 장면 제작: `runs/euno/worlds/steampunk/standing_goggles_20261012.png` (내장 이미지 생성 도구, 오른쪽 얼굴 구도).
- [x] 사용자 폴더명 변경 확인: 이후 Eunoh 자료의 저장 루트는 `runs/euno/`. 아래 이전 작업 기록의 `runs/eunoh/`는 당시 경로다.
- [x] 두 첨부 이미지를 인물·화풍 참고로 사용한 스팀펑크 시계공 작업실 장면 제작: `runs/eunoh/worlds/steampunk/clockmaker_20261012.png` (내장 이미지 생성 도구, 흑백 세밀 선화).
- [x] 창가·카세트 장면의 고개를 정면으로 돌린 수정본 제작: `runs/eunoh/worlds/1990s_citypop/window_cassette_20261012_v3.png` (내장 이미지 생성 도구, 원본 유지).
- [x] 1990년대 밤거리 장면 제작: `runs/eunoh/worlds/1990s_citypop/night_street_20261012.png` (내장 이미지 생성 도구).
- [x] 창가·카세트 장면의 셔츠 앞섶을 여민 수정본 제작: `runs/eunoh/worlds/1990s_citypop/window_cassette_20261012_v2.png` (내장 이미지 생성 도구, 원본 유지).
- [x] 새 요청의 두 첨부 이미지를 참고한 1990년대 시티팝 창가·카세트 장면 제작: `runs/eunoh/worlds/1990s_citypop/window_cassette_20261012.png` (내장 이미지 생성 도구, 인물 기준 왼쪽 눈썹 피어싱·왼쪽 눈 아래 점).
- [x] 변경된 채널 정체성 문서 반영.
- [x] `runs/eunoh/`에 `drafts/`, `reference/`, `worlds/` 생성, 기존 이미지 3개를 시안으로 복사(원본 유지).
- [x] Eunoh 얼굴 기준으로 사용자가 지정한 `eunoh_base2.jpg`를 `runs/euno/reference/`에 복사 (원본 유지).
- [ ] Eunoh 체형 기준 이미지 선택.
- [x] 1990년대 시티팝 배경 시안 제작: `runs/eunoh/worlds/1990s_citypop/scene_v1.png` (사용자가 지정한 drafts 인물 참고, 내장 이미지 생성 도구 사용).
- [x] 같은 시안의 손과 얼굴 좌우 특징 수정: `runs/eunoh/worlds/1990s_citypop/scene_v2.png` (오른쪽 얼굴에 보이던 점 제거, 왼쪽 눈 아래 점·왼쪽 눈썹 피어싱은 가려지는 구도).
- [x] 팔·손목 비율 조정: `runs/eunoh/worlds/1990s_citypop/scene_v3.png`. 사용자 좌우 설명은 화면을 보는 사람 기준이며, 눈썹 피어싱 추가 없이 수정.
- [x] 눈썹 피어싱 제거 및 실내 화분·표면 묘사 축소 시안: `runs/eunoh/worlds/1990s_citypop/scene_v4.png`.

- [x] Python 표준 라이브러리 기반 `scripts/prompt.py` 구현.
- [x] 기존 로컬 Gemma 연결 및 프롬프트 생성 동작 확인.
- [x] 저장된 이미지 생성 프롬프트·요청·응답·후보·평가 기록 정리.
- [x] 스타일 설정과 참조 설명 목록 초기화.
- [x] 음악 프롬프트를 GPT 대화 작성으로 전환하고 Gemma 도구의 음악·가사 기능 제거.
- [x] 과거 Gemma 음악 프롬프트 실행 폴더 9개 삭제(요청·응답·후보·프롬프트·생성 가사).
- [x] 첫 영상의 장면과 시각 방향 정하기.
- [x] 첫 영상용 바탕 이미지 제작 및 선택: `runs/eunoh_base_proportions_v3.png`.
- [x] 오른쪽 위 흑백 카세트 릴 회전·음원 반응 막대·현재 곡명 구현, MP4 미리보기 제작.
- [x] 음악을 결합한 20초 샘플 제작: `runs/playlist_261010/preview.mp4`.
- [x] 첫 전체 시안 출력: 1080p/24fps H.264 MP4, 8곡 1회 재생, 23분 7초.
- [x] 사용자 요청에 따라 8곡 전체를 총 3회 반복한 버전 출력: 1시간 9분 21.72초.
- [ ] 3회 반복 영상 최종 검토.
- [x] 두 번째 플레이리스트(261012) 렌더 스크립트 작성: 12곡을 다운로드 순서대로 연결하고, 채널명을 `BG TAPE`로 표기.
- [x] 261012 전체 영상 출력: 오버레이 수정본 `bg_tape_261012_v2.mp4`, 49분 5초, 12개 챕터.
- [ ] 261012 전체 영상 최종 검토.

## 현재 이미지 제작 자료

- 선택 이미지: `runs/eunoh_base_proportions_v3.png`.
- 이미지에 맞춘 재구성 프롬프트: `runs/eunoh_base_proportions_v3_prompt.txt`.
- 사용자 요청으로 나머지 이미지 제작 자료는 프로젝트 밖에 백업하고 정리했다. 이후 2026-10-12에 Gemma 음악 실행 기록과 그 안의 생성 가사도 사용자 요청으로 삭제했다. 음원·영상·Eunoh 이미지 자료는 유지했다.
- 선택 이미지는 투명 배경의 인물·노트북 바탕이며 테이프·막대·문구는 포함하지 않는다.

## 작업 원칙

- 새 사용자 요청을 출발점으로 삼는다.
- 이전 이미지의 프롬프트, 장면 설정, 취향·평가를 다음 작업의 지침으로 사용하지 않는다.
- 이미지에 대한 호불호나 선호 추정을 문서·설정에 기록하지 않는다.
- Eunoh 자료는 `runs/euno/`에 계속 추가한다. 사용자가 선택한 인물 참고만 명시적으로 사용하며, 폴더 전체를 자동 참조하지 않는다.
- 반복 등장하는 주인공은 Eunoh다. 얼굴 기준은 `runs/euno/reference/eunoh_base2.jpg`, 체형 기준은 아직 선택 전이다. 채널 화풍 기준(얇은 선화, 정면, 어깨 위, 흰 배경, 은은한 색, 16:9)은 `AGENTS.md`를 따르고, 시대·의상·소품은 장면별로 정한다.
- 큰 자동화 시스템을 먼저 만들지 않고 필요한 작업부터 진행한다.

## 기술 메모

`config/style.json`에는 2026-10-13 사용자가 확정한 채널 화풍 기준이 들어 있고, `references/catalog.json`은 빈 배열이다. 새 장면 설명만으로 dry-run이 가능하다.
음악 프롬프트와 요청받은 가사는 GPT와 대화에서 직접 작성한다. Gemma는 이미지 프롬프트 전용이다.
Gemma에는 명시적으로 조립된 텍스트만 전달하며 로컬 이미지나 과거 실행을 자동으로 읽지 않는다.
이미지 생성 API, Suno API, 웹 미리보기는 연결되어 있지 않다. 로컬 영상 출력은 `runs/playlist_261010/render.py`로 제작했다(FFmpeg, uv로 실행하는 Pillow·NumPy 사용). 기존 프롬프트 도구는 Python 표준 라이브러리 기반을 유지한다.

전체 시안: `runs/playlist_261010/legacy_code_tape_261010.mp4`. 곡 타임스탬프는 같은 폴더의 `tracklist.txt`. 원본 이미지는 유지하고 흰 배경에 합성했다. 곡 순서는 제안한 임시 순서이며, 반복·크로스페이드 없이 원본 음량으로 연결했다.

기존 LLM의 포트 8080을 재사용한다. 서비스를 종료하거나 같은 포트에 서버를 띄우지 않는다. 새 서버가 필요하면 머신 포트 규약과 점유를 먼저 확인한다.

## 3회 반복 영상

`runs/playlist_261010/legacy_code_tape_261010_3loops.mp4`: 기존 영상의 순서·그래픽을 유지해 총 3회 재생. 영상 스트림은 재압축 없이 복사하고, 음원은 원본 PCM을 3회 연결해 AAC로 인코딩했다. 총 24개 챕터를 포함하며, 설명용 타임스탬프는 `runs/playlist_261010/tracklist_3loops.txt`. 재생성 스크립트는 같은 폴더의 `loop_three.py`.

## 261012 플레이리스트

`runs/playlist_261012/bg_tape_261012_v2.mp4`: 이미지 `runs/eunoh/drafts/eunoh_right_face_wireless_pajamas.png`(1920폭으로 확대 후 위 40px 기준 1080 높이로 자름), 음원은 `~/Downloads`의 wav 12곡을 다운로드 순서대로 1회 재생. 1080p/24fps H.264, AAC 320k, 49분 5초, 12개 챕터. 타임스탬프는 `tracklist.txt`.

오버레이는 오른쪽 위에 둔다. 사용자 검토를 거쳐 정한 설정: 기존 시안의 약 72% 크기(`K = 0.72`), 고정 너비 칸(`PANEL_W_U`)에 긴 제목은 줄바꿈해서 칸이 아래로 늘어남, 약 65% 불투명 흰 배경(`PANEL_ALPHA = 166`), 주파수 막대 19개, 채널명 `BG TAPE`.

재생성은 `uv run --with pillow --with numpy python render.py --out <새 파일명>`. 디자인 확인은 `--frame 초`(정지 화면, `--title`로 임시 제목 시험 가능)와 `--preview 초`로 한다. 처음 렌더링한 `bg_tape_261012.mp4`는 중간에 덮어쓰다 멈춰서 18분까지만 남은 불완전 파일이다.
