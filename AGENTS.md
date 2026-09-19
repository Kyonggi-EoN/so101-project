# AGENTS.md

AI 코딩 에이전트를 위한 지침. 사람이 읽는 문서는 [README.md](README.md) 와 [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 이 리포가 무엇인가

동아리 SO-101 로봇팔 프로젝트. [lerobot](https://github.com/huggingface/lerobot) 을 `third_party/lerobot/` 에 **복사해 두고(vendoring)** 쓴다. 부원들이 코드를 읽으며 공부하는 것이 목적이다.

- 패키지 관리: `uv` (pip 아님)
- Python 3.12, Windows(PowerShell) 기준
- 기본 브랜치: `master`

---

## 권한 경계 — 먼저 읽을 것

**너는 메인테이너가 아니다.** 메인테이너는 `@jsjin7371` 이다.

### 자유롭게 작업해도 되는 곳

```
projects/          단, projects/_TEMPLATE/ 과 projects/README.md 는 제외
```

### 사용자가 명시적으로 요청하지 않는 한 수정 금지

| 경로 | 이유 |
|---|---|
| `third_party/` | lerobot 원본 복사본. 수정하면 다음 업데이트 때 소실된다 |
| `calibration/` | 로봇 하드웨어 기준값. 바꾸면 학습된 정책이 잘못 동작한다 |
| `pyproject.toml` · `uv.lock` | 전원의 환경 일치를 보장하는 파일 |
| `docs/` · `tools/` · `CONTRIBUTING.md` · `CODEOWNERS` · `.github/` | 공용 문서·설정 |
| `projects/_TEMPLATE/` | 부원이 복사해 쓰는 양식 |

이 경로를 고쳐야 할 것 같으면 **직접 고치지 말고 사용자에게 이유를 설명하고 확인을 받는다.**

`CODEOWNERS` + branch protection 으로 막혀 있어 승인 없이는 머지되지 않는다. 몰래 고쳐도 반영되지 않고 PR 만 지저분해진다.

---

## 명령어 규칙

### 항상 `uv run` 을 쓴다

```powershell
uv run lerobot-find-port          # O
uv run python script.py           # O
python script.py                  # X — 시스템 파이썬이 실행되어 패키지를 못 찾는다
pip install <패키지>               # X — 이 환경에 pip 자체가 없다
```

### 패키지 추가

`pyproject.toml` 을 직접 수정하지 않는다. 시험할 때는:

```powershell
uv pip install <패키지>
```

이것은 `.venv` 에만 반영되고 커밋되지 않는다. 정식 추가가 필요하면 사용자에게 요청한다.

### 작업 디렉터리

모든 명령은 리포 루트에서 실행한다. 학습 출력 경로(`outputs/train/...`)가 상대경로라 실행 위치에 의존한다.

---

## 파일 경로

| 무엇 | 위치 | 비고 |
|---|---|---|
| 캘리브레이션 | `calibration/robots/so_follower/`, `calibration/teleoperators/so_leader/` | `HF_LEROBOT_CALIBRATION` 또는 `--robot.calibration_dir` 로 지정 |
| 데이터셋·모델 캐시 | `~/.cache/huggingface/lerobot/` | 리포 밖. 수 GB |
| 학습 출력 | `outputs/` | `.gitignore` 처리됨 |

`third_party/lerobot/utils/constants.py` 에서 결정된다.

---

## 커밋하면 안 되는 것

`.gitignore` 가 막고 있지만 확인할 것.

```
outputs/  ·  *.mp4  ·  *.parquet  ·  .venv/  ·  local.ps1  ·  *.pem  ·  .env
third_party/*.egg-info/
```

`git add .` 전에 `git status` 로 확인한다.

---

## 브랜치와 커밋

```
feat/<깃허브-아이디>/<주제>        예: feat/jsjin7371/hand-tracking
```

- `master` 에 직접 커밋하지 않는다
- 브랜치 하나 = PR 하나 = 세미나 발표 하나
- 커밋 메시지는 무엇을 했는지 알아볼 수 있게 쓴다

---

## 프로젝트 결과물 기준

이 리포의 PR 심사 기준은 **"처음 보는 사람이 이것만 읽고 따라 할 수 있는가"** 다. 코드 동작만으로는 통과하지 못한다.

`projects/<프로젝트>/README.md` 에 6개 항목이 모두 있어야 한다.

| | 항목 |
|---|---|
| 1 | 무엇을 하는가 (사진/영상 포함) |
| 2 | 왜 만들었는가 |
| 3 | 실행 방법 — 복사해서 붙여 넣으면 되게 |
| 4 | 어떻게 동작하는가 |
| 5 | **막혔던 것과 해결 방법** |
| 6 | 한계와 다음에 할 것 |

양식은 `projects/_TEMPLATE/README.md` 에 있다. 복사해서 채운다.

### 문서 작성 시

- 사용자 고유값(`C:\Users\jsjin\...`, `COM5`, HuggingFace 아이디)을 문서에 박지 않는다. `<...>` 플레이스홀더로 쓰고 바로 아래에 채운 예시를 붙인다
- 5번 항목을 비우지 않는다. 에러 메시지는 원문 그대로 넣는다
- 대상 독자는 **프로그래밍 경험이 없는 신입**이다. 전문 용어는 처음 쓸 때 풀어 쓴다
- 길어지는 배경 설명은 `<details>` 로 접는다

---

## 검증

코드를 작성했으면 최소한 실행해 본다. 추측으로 "될 것이다" 라고 보고하지 않는다.

```powershell
uv run python -c "import lerobot, torch; print(lerobot.__version__, torch.__version__, torch.cuda.is_available())"
```

### lerobot 옵션을 문서에 쓸 때

**반드시 `third_party/lerobot/` 의 실제 코드에서 확인한다.** 기억이나 다른 버전의 문서를 근거로 쓰지 않는다. 이 리포의 lerobot 은 특정 커밋에 고정돼 있어 상위 버전과 다를 수 있다.

```powershell
uv run lerobot-<명령> --help
```

옵션은 코드의 `@dataclass` 에서 자동 생성된다. 해당 `scripts/lerobot_*.py` 를 직접 읽는 것이 가장 정확하다.

---

## 하드웨어를 다룰 때

로봇팔은 **동아리에 한 대뿐**이고 모터가 물리적으로 파손될 수 있다.

- 모터에 토크를 거는 코드(`--move`, `send_action` 등)를 사용자 확인 없이 실행하지 않는다
- 로봇에 정책을 실행하는 명령(`lerobot-rollout`)은 `--duration` 을 짧게 잡아 제안한다. 기본값 0 은 무한이다
- 캘리브레이션(`lerobot-calibrate`)을 임의로 제안하지 않는다. 기존 값을 덮어써서 학습된 정책과 어긋나게 만든다

---

## 사용자에게 확인해야 하는 상황

- 보호 경로를 수정해야 할 때
- 새 패키지를 정식으로 추가해야 할 때
- lerobot 버전을 올려야 할 때 (`tools/update_lerobot.ps1`)
- 로봇을 실제로 움직이는 명령을 실행할 때
- `git push --force`, `git reset --hard` 등 되돌릴 수 없는 작업

---

## 참고 문서

| 문서 | 내용 |
|---|---|
| [docs/1_setup.md](docs/1_setup.md) | 설치, GPU 설정 |
| [docs/2_codebase.md](docs/2_codebase.md) | 프로젝트 구조 |
| [docs/3_commands.md](docs/3_commands.md) | uv 사용법, lerobot 버전 올리기 |
| [docs/4_git.md](docs/4_git.md) | git 기초 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 작업 규칙, PR 3단계 |
| [third_party/UPSTREAM.md](third_party/UPSTREAM.md) | 현재 lerobot 버전 |
