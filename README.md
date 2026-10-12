# Legacy Code Tape

시대와 세계를 자유롭게 여행하며, 도착한 세계의 소리를 우리 일상의 배경음악으로 담는 플레이리스트 채널.
음악은 Suno에서 제작한다. 주인공 Eunoh는 여러 시대와 세계에 등장하며, 각 장면은 새 요청부터 정한다.

> We can go anywhere.
> A neon alley that never sleeps, a sky full of airships, the small room of someone in the 1500s.
>
> The sounds of the world we arrive in, as the background music of our day.
>
> -
> 📼 The tape is rolling.
> Where will we settle in today?

주인공 이미지 모음은 `runs/eunoh/`에 둔다. `drafts/`에는 얼굴 등 시안, `reference/`에는 사용자가 선택한 인물 기준, `worlds/`에는 시대별 장면을 추가한다. 로컬 전용이며 도구가 자동으로 읽지는 않는다.

## 현재 가능한 것

Python 표준 라이브러리로 구현한 `scripts/prompt.py`가 기존 로컬 Gemma에 설명을 전달하고 이미지 프롬프트 후보를 저장한다.

```sh
python3 scripts/prompt.py --help
python3 scripts/prompt.py --brief '<새 장면 설명>' --dry-run
python3 scripts/prompt.py --brief '<새 장면 설명>' --count 1
```

후보 수는 `--count`로 1~6개를 지정한다. 실행별 `runs/` 폴더에 요청(`request.json`), 원본 응답(`response.json`), 검증된 후보(`candidates.json`), 복사용 영어 이미지 프롬프트(`prompt-01.txt` 등)를 저장한다. 검증에 실패해도 원본 응답은 남는다.

## 음악 프롬프트

Suno 음악 프롬프트는 GPT와 대화에서 직접 만든다. 한국어 상황 설명과 복사 가능한 영어 스타일 프롬프트를 사용하며, 가사는 요청할 때만 별도로 작성한다. Gemma 도구는 이미지 프롬프트 전용이다.

서비스 없이 검사: `python3 -m unittest discover -s tests -v`. 실제 Gemma 호출은 별도 수동 확인이다.

기본 주소는 `http://127.0.0.1:8080/v1`이다. `GEMMA_BASE_URL`과 `GEMMA_MODEL` 환경 변수로 변경할 수 있다. 도구는 서버를 시작하거나 종료하지 않는다.

- `config/style.json`: 현재 비어 있는 선택적 스타일 문맥.
- `references/catalog.json`: 현재 비어 있는 참조 설명 목록. 로컬 이미지 픽셀은 자동 전달하지 않는다.
- `references/local/`: 로컬 참조 이미지 파일, Git 제외.
- `runs/`: 실행별 요청·원본 응답·후보·프롬프트와 이미지 파일, Git 제외.

이미지 생성 API, Suno API, 웹 편집기, 영상 출력은 프로젝트에 연결되어 있지 않다.
현재 상태와 다음 단계는 [작업 인계](docs/NEXT_STEPS.md)를 참고한다.
