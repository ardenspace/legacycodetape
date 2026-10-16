# Legacy Code Tape

A playlist channel that travels across eras and imagined worlds, bringing the sounds of each destination into everyday life.

## Project direction
- We can go anywhere: the sounds of each world become the background music of our day.
- Eunoh is the recurring protagonist across eras and worlds. Collect image drafts in `runs/euno/drafts/`; only user-selected identity references belong in `runs/euno/reference/`. World-specific scenes belong in `runs/euno/worlds/`.
- Music is made with Suno.
- Titles describe music and atmosphere; optional lore belongs in descriptions.
- Begin each world and scene from the user's next brief. Use explicitly selected Eunoh images for character continuity; clothing, props and settings may change across worlds.
- Do not carry prior image prompts, scene concepts or preference/evaluation notes into new work.
- Do not record likes/dislikes or infer persistent visual preferences from experiments.
- Build incrementally. No full automation platform, upload pipeline, new backend or asset database yet.

## Eunoh identity — explicit user rules
- 사용자 확정 얼굴 참고: `runs/euno/reference/mono/eunoh_base2.jpg` (2026-10-12, “우리 은오는 이렇게 생겼어”). Eunoh 제작 시 이 이미지를 얼굴 정체성 참고로 명시적으로 사용한다. 의상·배경은 고정하지 않는다.
- Eunoh는 여성이다 (2026-10-13 사용자 확인). 체형·어깨 등 몸은 여성 비율로 그린다. 이 사실을 이유로 확정된 얼굴을 바꾸지 않는다.
- 좌우는 화면을 보는 사람 기준으로 명시한다. 화면 기준 오른쪽 눈썹에 피어싱, 오른쪽 눈 아래에 점 하나가 있다 (인물 기준 왼쪽).
- 화면 기준 왼쪽 눈 아래에 점을 넣거나 왼쪽 눈썹에 피어싱을 복제하지 않는다. 반측면·측면에서도 인물의 해부학적 위치를 유지하고, 해당 부위가 가려지면 반대편으로 옮겨 그리지 않는다.
- 사용자 확정 옆모습 참고 (2026-10-13): `runs/euno/reference/face/profile_left_v2.png`(화면 왼쪽을 봄, 표시 보임), `runs/euno/reference/face/profile_right_v2.png`(화면 오른쪽을 봄, 표시 없음). 옆모습을 그릴 때 같은 방향의 참고를 첨부한다.
- 옆모습에서 보이는 쪽 (2026-10-13 사용자 확인): 얼굴이 화면 오른쪽을 향하면 인물의 오른쪽 얼굴이 보이므로 점·눈썹 피어싱이 없고, 보이는 귀에는 링 하나만 있다. 얼굴이 화면 왼쪽을 향하면 인물의 왼쪽 얼굴이 보이므로 눈썹 피어싱(구슬 두 개)과 눈 아래 점이 보이고, 보이는 귀에는 링과 작은 귀걸이 두 개가 있다.
- Eunoh 이미지 생성·수정 프롬프트에 이 특징과 좌우 기준을 명시하고, 결과에서 위치를 확인한다. 이전 작업 기록과 충돌하면 이 사용자 확정 규칙을 우선한다.
- These are user-defined character identity facts, not inferred visual preferences; they persist across worlds.

## Channel image standard — explicit user rules
- 참고 폴더 구성 (2026-10-17 사용자 정리): `runs/euno/reference/face/`에는 채널 화풍의 은오 얼굴 참고(정면 `direction1_front_v1.png`, 16:9 `front_16x9_v6.png`, 옆모습 `profile_left_v2.png`·`profile_right_v2.png`)를, `runs/euno/reference/mono/`에는 흑백 선화 참고(`eunoh_base2.jpg` 등)를 둔다. 은오를 그릴 때는 `face/front_16x9_v6.png`를 화풍·구도·얼굴 참고로 우선 첨부한다.
- 사용자 확정 화풍 참고: `references/local/channel_style/channel_style_front_bust_20261013.png` (2026-10-13, “이 정면샷을 우리의 레퍼런스로 두자”). 원본은 `runs/euno/drafts/style_2026-10-13/direction1_front_v1.png`.
- 사용자 확정 16:9 참고: `references/local/channel_style/channel_style_front_bust_16x9_20261013.png` (2026-10-13, “이 그림도 레퍼런스로 두자”, 1920x1080). 원본은 `runs/euno/drafts/style_2026-10-13/front_16x9_v6.png`. 영상용 구도·어깨·여백의 기준으로 쓴다.
- 생성 편집을 여러 번 이어서 하면 노이즈가 쌓인다. 수정할 때는 원본에서 한 번만 생성하고, 바꾸지 않는 부분은 원본 픽셀을 다시 합성한다. 확대는 되도록 피한다.
- 기준: 얇고 섬세한 선화, 정면을 바라보는 구도, 어깨 위까지만 보이는 구도, 가로 16:9 (영상용, 예: 1920x1080).
- 어깨는 넓고 편안하게 바깥쪽으로 완만히 내려가다가 팔로 꺾이기 전에 화면 아래 가장자리(가로 약 10%, 90% 지점)에서 잘린다. 위팔은 보이지 않는다 (2026-10-13 사용자 승인, 위 16:9 참고 이미지와 같다).
- 채널에 반영할 때는 배경을 흰색으로 두고, 선화는 그대로 유지하면서 인물에만 은은하게 색을 입힌다 (2026-10-13 사용자 요청).
- 인물은 바뀔 수 있다. 이 참고 이미지는 화풍·구도 기준이며, Eunoh 얼굴 정체성 기준은 위 `eunoh_base2.jpg`다. 의상·소품으로 세계를 표현한다.
- The same rules are in `config/style.json` so Gemma receives them. These are user-defined standards, not inferred preferences.
- 이 기준은 "이전 프롬프트·장면 설정을 새 작업에 가져오지 않는다" 원칙의 예외다. 사용자가 확정한 채널 기준이므로 새 작업마다 적용한다. 이전 시안의 프롬프트와 의상·소품은 여전히 가져오지 않는다.

### 새 인물 이미지 요청을 받으면
1. 16:9 기준 이미지(`channel_style_front_bust_16x9_20261013.png`)를 화풍·구도 참고로 이미지 생성 도구에 첨부한다. 얼굴·머리·의상은 이 이미지에서 가져오지 않는다고 프롬프트에 명시한다.
2. 인물의 외모·의상·소품은 사용자의 새 요청대로 그린다. 위 기준(얇은 선화, 정면, 어깨 구도, 흰 배경, 은은한 색)은 그대로 지킨다.
3. 인물이 Eunoh일 때만 `eunoh_base2.jpg`를 얼굴 참고로 함께 첨부하고, 위 Eunoh 정체성 규칙(여성, 화면 기준 오른쪽 눈썹 피어싱·오른쪽 눈 아래 점)을 적용해서 결과의 위치를 확인한다. 다른 인물에는 이 규칙을 적용하지 않는다. 인물이 누구인지 불분명하면 먼저 묻는다.
4. 처음부터 16:9로 생성하고, 최종 파일은 정확히 1920x1080으로 맞춘다. 확대와 편집 반복은 최소화한다.
5. `runs/euno/drafts/` 아래 날짜 폴더에 덮어쓰지 않고 저장하고, 같은 이름의 `_prompt.txt`(정확한 프롬프트)와 처리 기록을 함께 남긴다. 보고한 뒤 멈추고 사용자의 선택을 기다린다.

## Planning and handoff
- Read `docs/NEXT_STEPS.md` before continuing. It records completion status, proposed phases, acceptance criteria and unresolved decisions.
- Update its checkboxes as work is actually completed; do not treat proposed defaults as user-approved requirements.

## Implementation
- Python standard library only for the initial prompt tool: `python3 scripts/prompt.py --help`.
- Gemma is for image prompts only, using `scripts/prompt.py`. Pass current scene context explicitly; prior runs are not automatically read.
- Write music/Suno prompts directly with GPT in conversation, not through Gemma. Return Korean situation labels/descriptions and copyable English Suno prompts; never assume a fixed genre.
- Generate lyrics only when requested. Keep English style prompts and lyrics separate; follow the requested language or brief, defaulting to Korean.
- `config/style.json`: style context sent to Gemma; holds the channel image standard above.
- `references/catalog.json`: optional reference notes sent to Gemma; currently empty. Local image pixels are NOT sent by the tool.
- `references/local/`: user references, local only and ignored by Git.
- `runs/`: requests, raw responses, candidates and copyable English prompts; local only.
- Reuse the existing Gemma endpoint on port 8080. Never stop/restart it or bind a new server there.
- No changes to auto-shorts are required. Keep this project independent.
- No image-generation or Suno API integration is configured. Do not claim otherwise.
- Before any future dev server, check machine and project port rules and inspect the selected port.

## Checks
- Dry-run prompt assembly without services.
- Validate candidate output and save raw responses so failures remain inspectable.
- Real model calls are manual smoke checks, not automated tests.
