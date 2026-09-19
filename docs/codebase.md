# lerobot 코드 지도

`third_party/lerobot/` 에는 `.py` 파일이 537개 있다. 처음부터 읽으면 길을 잃는다.
이 문서는 **어디부터 봐야 하는지**를 정리한 것이다.

> `third_party/lerobot/` 은 **읽기 전용**이다. 수정은 관리자만 한다.
> 다만 `print` 를 찍어보는 건 자유다 — 아래 [직접 찍어보기](#직접-찍어보기) 참고.

---

## 왜 코드가 리포 안에 있나

lerobot 은 보통 의존성으로 설치해서 `.venv\` 안에 숨겨 둔다.
우리는 **모두가 코드를 읽으면서 개발하기 위해** 일부러 리포에 복사해 두었다.
덕분에 GitHub 에서 링크를 걸 수 있고, 에디터 파일 트리에 바로 보인다.

버전은 `third_party/UPSTREAM.md` 에 커밋 해시로 고정돼 있다.

---

## 큰 그림

```
third_party/lerobot/
├─ scripts/         터미널 명령어 19개의 실체          8,100줄
├─ robots/          로봇 하드웨어 (so_follower 등)     8,400줄
├─ teleoperators/   조작 장치 (so_leader, phone 등)    6,900줄
├─ motors/          서보 통신 (feetech, dynamixel)     5,300줄
├─ cameras/         카메라 (opencv, realsense)         3,100줄
├─ datasets/        녹화·저장·로딩                    14,200줄
├─ processor/       정규화 / 파이프라인                7,500줄
├─ policies/        정책 모델 30여 종 (act 포함)      60,000줄
├─ rollout/         추론 실행                          6,000줄
├─ configs/         설정 dataclass, CLI 파서           2,700줄
└─ utils/           상수, 타이머, 키 입력              6,000줄
```

`policies/` 가 전체의 절반이지만 **우리가 쓰는 건 `policies/act/` 뿐**이다. 나머지는 다른 정책들이다.

---

## 명령어 → 파일

`pyproject.toml` 의 `[project.scripts]` 가 명령어 이름과 파일을 연결한다.

```toml
lerobot-teleoperate = "lerobot.scripts.lerobot_teleoperate:main"
#                      └────── 모듈 경로 ──────┘  └함수┘
```

| 명령어 | 파일 (`third_party/lerobot/scripts/`) | 줄수 |
|---|---|---|
| `lerobot-find-port` | `lerobot_find_port.py` | 72 |
| `lerobot-setup-motors` | `lerobot_setup_motors.py` | 88 |
| `lerobot-calibrate` | `lerobot_calibrate.py` | 110 |
| `lerobot-find-cameras` | `lerobot_find_cameras.py` | 309 |
| `lerobot-teleoperate` | `lerobot_teleoperate.py` | 301 |
| `lerobot-record` | `lerobot_record.py` | 592 |
| `lerobot-replay` | `lerobot_replay.py` | 150 |
| `lerobot-train` | `lerobot_train.py` | 981 |
| `lerobot-rollout` | `lerobot_rollout.py` | 279 |

---

## CLI 인자가 처리되는 방식

명령어 한 줄이 **dataclass 트리에 1:1로 매핑**된다. `draccus` 라이브러리가 한다.

### 1) 설정 dataclass 가 곧 옵션 이름

`scripts/lerobot_teleoperate.py`:

```python
@dataclass
class TeleoperateConfig:
    teleop: TeleoperatorConfig
    robot: RobotConfig
    fps: int = 60

@parser.wrap()
def teleoperate(cfg: TeleoperateConfig):
    ...
```

필드 이름이 그대로 옵션이 되고, 중첩은 점(`.`)으로 이어진다.

```
--fps=30            →  TeleoperateConfig.fps
--robot.port=COM6   →  TeleoperateConfig.robot.port
```

### 2) `--robot.type` 이 클래스를 고른다

`robots/config.py`:

```python
class RobotConfig(draccus.ChoiceRegistry, abc.ABC):   # 등록소
```

`robots/so_follower/config_so_follower.py`:

```python
@RobotConfig.register_subclass("so101_follower")      # 이름표
@RobotConfig.register_subclass("so100_follower")
class SOFollowerRobotConfig(RobotConfig, SOFollowerConfig):
```

`RobotConfig` 는 추상 클래스라 그 자체로는 못 만든다.
`--robot.type=so101_follower` 를 보고 등록소에서 `SOFollowerRobotConfig` 를 꺼낸 뒤, 그 클래스의 필드로 나머지 인자를 채운다.

`port: str` 에 기본값이 없어서 **`--robot.port` 를 빼먹으면 에러**가 나는 것도 여기서 정해진다.

### 3) `@parser.wrap()` 이 얹는 것

`configs/parser.py`:

| 기능 | 설명 |
|---|---|
| `--help` 범위 조정 | `--robot.type=...` 을 같이 주면 그 로봇 전용 옵션만 보여준다 |
| `--config_path` | JSON/YAML 파일이나 HF repo_id 에서 설정을 읽는다. **CLI 인자가 파일 값을 덮어쓴다** |
| 플러그인 로딩 | 외부 패키지의 로봇/정책을 등록소에 추가 |

학습 재개(`--config_path=... --resume=true --steps=200000`)에서 스텝만 바꿔 늘릴 수 있는 것이 두 번째 기능 덕분이다.

---

## 파일 경로가 정해지는 곳

전부 `utils/constants.py` 에서 결정된다.

```python
default_cache_path     = Path(HF_HOME) / "lerobot"            # ~/.cache/huggingface/lerobot
HF_LEROBOT_HOME        = getenv("HF_LEROBOT_HOME",        default_cache_path)
HF_LEROBOT_HUB_CACHE   = HF_LEROBOT_HOME / "hub"
HF_LEROBOT_CALIBRATION = getenv("HF_LEROBOT_CALIBRATION", HF_LEROBOT_HOME / "calibration")
```

| 무엇 | 기본 위치 | 우리 설정 |
|---|---|---|
| 캘리브레이션 | `~/.cache/huggingface/lerobot/calibration/` | **리포의 `calibration/`** (`local.ps1` 의 환경변수) |
| 데이터셋·모델 캐시 | `~/.cache/huggingface/lerobot/` | 기본 유지 (수 GB, 여러 프로젝트가 공유) |
| 학습 출력 | `outputs/train/<날짜>/<시각>_<job>` | 기본 유지 (`.gitignore` 처리됨) |

학습 출력은 **상대경로**(`Path("outputs/train")`)라 명령을 실행한 폴더 기준이다. 항상 리포 루트에서 실행할 것.

---

## 공부 순서

이미 돌려본 명령을 따라가는 것이 가장 빠르다. 결과를 아니까 코드가 뭘 하는지 대응이 된다.

### 1단계 — 텔레오퍼레이션 (여기부터)

`lerobot-teleoperate` 하나에 로봇·리더·카메라·제어 루프가 전부 들어 있다.

```
scripts/lerobot_teleoperate.py        teleop_loop() — 30Hz 루프 한 바퀴 ← 시작점
├─ teleoperators/so_leader/so_leader.py   get_action()      리더 팔 관절 읽기
├─ robots/so_follower/so_follower.py      get_observation() / send_action()
│   └─ motors/motors_bus.py               sync_read / sync_write  모터 통신
│       └─ motors/feetech/                STS3215 프로토콜
├─ cameras/opencv/camera_opencv.py        read_latest()
└─ utils/cycle_timer.py                   "Control loop is running slower" 경고의 출처
```

### 2단계 — 녹화

```
scripts/lerobot_record.py       1단계 루프 + 프레임 저장 + 키 입력
datasets/lerobot_dataset.py     에피소드 → parquet + mp4
utils/keyboard_input.py         녹화 중 키 처리
```

### 3단계 — 추론

```
scripts/lerobot_rollout.py      정책이 리더 팔 자리를 대신한다
rollout/configs.py              전략 등록: base / sentry / highlight / episodic / dagger
rollout/strategies/             각 전략 구현
processor/pipeline.py           입력 정규화 → 모델 → 출력 역정규화
policies/act/modeling_act.py    ACT 모델 본체
```

### 4단계 — 학습

```
scripts/lerobot_train.py        학습 루프
configs/train.py                하이퍼파라미터, 체크포인트 저장 조건
```

---

## 직접 찍어보기

`third_party/lerobot/` 은 **editable 설치**라 파일을 고치면 즉시 반영된다.
`.venv\` 안에 사본이 없고, 경로 파일 하나가 `third_party/` 를 가리킨다.

```
.venv\Lib\site-packages\__editable__.lerobot-0.6.2.pth
  → C:\...\so101_project\third_party
```

그래서 값이 실제로 어떻게 생겼는지 보려면 `print` 를 넣고 그냥 돌리면 된다.

```python
# third_party/lerobot/scripts/lerobot_teleoperate.py 안 어딘가
print("action:", action)
```

**끝나면 반드시 되돌린다.**

```powershell
git diff third_party/          # 내가 뭘 건드렸는지
git checkout -- third_party/   # 전부 원상복구
```

`third_party/` 는 `CODEOWNERS` 로 보호돼 있어서 실수로 커밋해도 머지되지 않지만, 되돌려 두는 것이 예의다.

### 에디터 팁

| 조작 | 하는 일 |
|---|---|
| `F12` | 커서 위 함수의 정의로 이동 |
| `Alt` + `←` | 이전 위치로 돌아오기 |
| `Shift` + `F12` | 이 함수를 쓰는 모든 곳 찾기 |
| `Ctrl` + `Shift` + `F` | 전체 검색 |

`robot.send_action()` 에서 `F12` 를 계속 누르면 시리얼 포트에 바이트를 쓰는 곳까지 내려갈 수 있다. 한 번 해보면 구조가 잡힌다.

---

## 로봇 없이 할 수 있는 것

팔은 하나뿐이라 순서를 기다려야 한다. 그동안 할 수 있는 것들:

- **데이터셋 읽기** — Hub 에서 받아서 `datasets/` 코드로 프레임을 꺼내 보기
- **학습** — GPU 만 있으면 된다
- **프로세서 파이프라인** — 정규화가 실제로 어떤 숫자를 만드는지
- **카메라 모듈** — 웹캠 하나로 `cameras/opencv/` 동작 확인
