# Legacy Code Tape

소프트웨어·전자·기계 등 무언가를 만드는 사람들을 위한 플레이리스트 제작 프로젝트.
음악은 Suno에서 제작한다. 시각 방향은 새 요청부터 정한다.

## 현재 가능한 것

Python 표준 라이브러리로 구현한 `scripts/prompt.py`가 기존 로컬 Gemma에 설명을 전달하고 이미지 또는 상황별 Suno 음악 프롬프트 후보를 저장한다.

```sh
python3 scripts/prompt.py --help
python3 scripts/prompt.py --brief '<새 장면 설명>' --dry-run
python3 scripts/prompt.py --brief '<새 장면 설명>' --count 1
```

## 상황별 Suno 프롬프트

음악 요청은 `--mode music`으로 실행한다. 한국어 상황 이름·설명과 Suno에 복사할 영어 프롬프트를 출력한다. 장르를 고정하지 않으며 `--genre`를 생략하면 요청에 맞게 제안한다. 기본은 보컬 없는 음악이고, 보컬이 필요하면 `--vocals vocals` 또는 요청문으로 지정한다. 가사는 `--lyrics`로 요청할 때만 생성하며 음원은 생성하지 않는다.

```sh
python3 scripts/prompt.py --mode music --genre 'jazzhop' --brief '작은 버그를 해결하고 흐름을 타는 개발자의 오후' --count 2
python3 scripts/prompt.py --mode music --genre 'drum and bass' --brief '해커톤 마지막 두 시간, 빠르고 추진력 있는 작업 음악' --count 3
python3 scripts/prompt.py --mode music --brief '퇴근 후 개인 프로젝트, 서로 다른 장르로 제안' --count 6 --dry-run
```

후보 수는 1~6개다. 각 후보는 상황에 맞춰 템포·악기·리듬·질감·에너지·전개를 제안한다. 음악 모드는 이미지 스타일 설정과 참조 목록을 읽지 않는다. 이전 실행도 자동으로 읽지 않으므로 변주할 기존 프롬프트는 `--brief`나 `--brief-file`에 직접 포함한다.

실행별 `runs/` 폴더에 `request.json`, `response.json`, `candidates.json`, 복사용 `prompt-01.txt` 등을 저장한다. 모델 출력 형식이 잘못되면 저장된 원본 응답으로 확인할 수 있다.

### 필요할 때 가사 함께 만들기

`--lyrics`를 붙이면 자동으로 보컬 곡을 요청하고, 영어 스타일 프롬프트와 창작 가사를 별도로 출력한다. `--lyrics-language`로 가사 언어를 지정할 수 있다. 생략하면 요청문에 명시된 언어를 따르고, 언어가 없으면 한국어를 사용한다. 장르만으로 가사 언어를 고정하지 않는다.

```sh
python3 scripts/prompt.py --mode music --genre J-pop --lyrics --lyrics-language Japanese --brief '퇴근길, 내일을 기대하는 밝은 노래' --count 1
python3 scripts/prompt.py --mode music --genre pop --lyrics --lyrics-language English --brief '멀어진 친구에게 먼저 연락하는 용기, 짧은 벌스와 기억에 남는 후렴' --count 2
```

스타일은 `prompt-01.txt`, 가사는 `lyrics-01.txt`처럼 같은 번호로 저장된다. 가사에는 `[Verse 1]`, `[Chorus]` 등의 구분과 줄바꿈을 포함하도록 요청한다. 길이·구성·주제는 요청문에 적는다. `--vocals vocals`만 사용하면 보컬 방향만 제안하고 가사는 쓰지 않는다. `--lyrics`와 `--vocals instrumental`은 함께 사용할 수 없다.

서비스 없이 검사: `python3 -m unittest discover -s tests -v`. 실제 Gemma 호출은 별도 수동 확인이다.

기본 주소는 `http://127.0.0.1:8080/v1`이다. `GEMMA_BASE_URL`과 `GEMMA_MODEL` 환경 변수로 변경할 수 있다. 도구는 서버를 시작하거나 종료하지 않는다.

- `config/style.json`: 현재 비어 있는 선택적 스타일 문맥.
- `references/catalog.json`: 현재 비어 있는 참조 설명 목록. 로컬 이미지 픽셀은 자동 전달하지 않는다.
- `references/local/`: 로컬 참조 이미지 파일, Git 제외.
- `runs/`: 실행별 요청·원본 응답·후보·프롬프트와 이미지 파일, Git 제외.

이미지 생성 API, Suno API, 웹 편집기, 영상 출력은 프로젝트에 연결되어 있지 않다.
현재 상태와 다음 단계는 [작업 인계](docs/NEXT_STEPS.md)를 참고한다.
