# 2. 프로젝트 구조

이 프로젝트에 **무엇이 어디 있고, 누가 고칠 수 있는지** 정리한 문서다.

로봇을 실제로 움직이는 방법은 `projects/` 의 기초 학습 문서에 있다.

---

## 이 프로젝트는 두 부분으로 되어 있다

```
① 우리가 만드는 것        ② 빌려 쓰는 것
   projects/                third_party/lerobot/
   (자유롭게 작업)           (읽기만, 수정 금지)
```

**lerobot** 은 로봇팔을 제어하는 프로그램 묶음이다. Hugging Face 라는 회사가 만들어 공개했고, 우리는 그걸 가져다 쓴다. 우리 팔(SO-101)을 움직이는 명령어들이 전부 여기서 나온다.

보통은 이런 걸 컴퓨터 구석에 설치해 두고 쓰는데, **우리는 일부러 프로젝트 폴더 안에 넣어 두었다.** 부원들이 코드를 직접 열어 보면서 공부하라는 뜻이다.

---

## 폴더 하나씩

```
so101_project/
│
├─ projects/             ★ 여기가 작업 구역. 자유롭게 만들고 고친다
│
├─ third_party/          빌려 온 lerobot 코드. 읽기만 한다
│  └─ lerobot/             파일 537개
│
├─ calibration/          로봇팔의 "기준값" 파일
│
├─ docs/                 지금 보고 있는 문서들
│
├─ tools/                관리용 도구
│
├─ pyproject.toml        필요한 패키지 목록
├─ uv.lock               그 패키지들의 정확한 버전
│
└─ .venv/                uv sync 가 만든 패키지 보관함 (건드릴 필요 없음)
```

### 고칠 수 있는 곳 / 없는 곳

| 폴더 | 누가 |
|---|---|
| `projects/` | **전원** — 자유 |
| 나머지 전부 | 메인테이너만 |

> **메인테이너**는 이 프로젝트를 관리하는 사람이다. 코드 검토와 `master` 브랜치 관리를 맡는다.
> 현재는 `@jsjin7371`. 자세한 역할과 작업 규칙은 `CONTRIBUTING.md` 에 있다.

메인테이너 구역을 건드린 변경은 **메인테이너가 승인해야 반영된다.** GitHub 가 자동으로 막아 준다.

실수로 고쳤더라도 문제없다. 반영이 안 될 뿐이고, 되돌리는 방법은 아래에 있다.

---

## 각 폴더가 하는 일

### `projects/` — 작업 구역

각자 만드는 것들이 여기 들어간다. 프로젝트마다 폴더를 하나씩 만든다.

```
projects/
└─ 01-무슨무슨-프로젝트/
   ├─ README.md      무엇을 하는 프로젝트인지
   └─ ...
```

### `third_party/lerobot/` — 빌려 온 코드

로봇을 움직이는 프로그램 본체다. 파일이 537개나 되지만 **전부 이해할 필요는 없다.**

```
lerobot/
├─ scripts/         우리가 터미널에 치는 명령어들의 실체
├─ robots/          로봇팔 제어
├─ teleoperators/   조종 장치 (leader 팔 등)
├─ motors/          모터와 통신
├─ cameras/         카메라
├─ datasets/        녹화한 데이터 저장·읽기
├─ policies/        인공지능 모델 (우리는 ACT 라는 것 하나만 쓴다)
├─ rollout/         학습한 인공지능으로 로봇 움직이기
├─ processor/       숫자 변환 처리
├─ configs/         설정 다루기
└─ utils/           잡다한 도구들
```

어느 버전을 쓰는지는 `third_party/UPSTREAM.md` 에 적혀 있다. 원본이 계속 업데이트되지만, **우리는 한 시점에 고정해 두고 메인테이너가 확인한 뒤에만 올린다.** 그래야 갑자기 안 되는 일이 안 생긴다.

### `calibration/` — 로봇팔 기준값

로봇 관절이 "어디가 0도인지"를 적어 둔 파일이다.

이 값이 바뀌면 **똑같은 인공지능이 다른 자세로 움직인다.** 녹화한 데이터도, 학습된 모델도 전부 이 기준으로 만들어졌기 때문이다.

그래서 프로젝트 폴더에 넣고 공유한다. 덕분에 새로 온 사람도 기준 잡는 작업 없이 바로 로봇을 움직일 수 있다.

### `pyproject.toml` 과 `uv.lock`

```
pyproject.toml   "numpy 는 2.0 이상 2.3 미만이면 된다"      ← 범위
uv.lock          "numpy 2.2.6 을 쓴다"                    ← 딱 하나로 확정
```

`uv sync` 는 `uv.lock` 을 보고 설치한다. 그래서 **모든 부원이 완전히 같은 환경**을 갖게 된다. "저는 되는데요" 가 안 생기는 이유다.

### `tools/update_lerobot.ps1`

빌려 온 lerobot 코드를 새 버전으로 갈아 끼우는 도구다. **메인테이너만 쓴다**. 자세한 건 [3_commands.md](3_commands.md) 에 있다.

---

## 명령어와 파일의 관계

터미널에 치는 명령어 하나하나가 **실제로는 파이썬 파일 하나**다. 전부 `third_party/lerobot/scripts/` 안에 있다.

| 터미널에 치는 것 | 실행되는 파일 |
|---|---|
| `lerobot-find-port` | `lerobot_find_port.py` |
| `lerobot-setup-motors` | `lerobot_setup_motors.py` | 
| `lerobot-calibrate` | `lerobot_calibrate.py` | 
| `lerobot-find-cameras` | `lerobot_find_cameras.py` |
| `lerobot-teleoperate` | `lerobot_teleoperate.py` | 
| `lerobot-record` | `lerobot_record.py` | 
| `lerobot-replay` | `lerobot_replay.py` | 
| `lerobot-train` | `lerobot_train.py` | 
| `lerobot-rollout` | `lerobot_rollout.py` | 

궁금한 명령어가 있으면 그 파일을 열어 보면 된다. **`lerobot-teleoperate` 가 301줄로 짧고 내용이 알차서 첫 독서로 좋다.**

<details>
<summary>명령어 뒤에 붙이는 옵션(--robot.port 같은 것)은 어디서 오나</summary>

옵션 목록을 사람이 따로 적어 두는 게 아니라, **코드에 적힌 설정 항목에서 자동으로 만들어진다.**

`lerobot_teleoperate.py` 를 열면 이런 게 있다.

```python
class TeleoperateConfig:
    teleop: TeleoperatorConfig
    robot: RobotConfig
    fps: int = 60
```

여기 적힌 이름이 그대로 옵션이 된다.

```
--fps=30             →  fps
--robot.port=COM6    →  robot 안의 port
```

`fps` 는 `= 60` 이라는 기본값이 있어서 안 써도 되고, `port` 는 기본값이 없어서 **꼭 써야 한다.**

그래서 옵션이 궁금할 땐 문서보다 그 파일을 보는 게 정확하다. 또는:

```powershell
uv run lerobot-teleoperate --help
```
</details>

---

## 파일이 저장되는 위치

프로그램이 만드는 파일들이 어디 가는지.

| 무엇 | 어디에 |
|---|---|
| 로봇 기준값 | 프로젝트의 `calibration/` |
| 녹화한 데이터, 내려받은 모델 | `C:\Users\<윈도우-사용자-이름>\.cache\huggingface\lerobot\` |
| 학습 결과 | 프로젝트의 `outputs/` |

**녹화 데이터만 프로젝트 밖에 저장된다.** 수 GB 라 프로젝트에 넣으면 너무 커지기 때문이다.

`outputs/` 는 **명령을 실행한 폴더 기준**으로 만들어진다. 그래서 항상 `so101_project` 폴더에서 실행해야 한다. (`outputs/` 와 녹화 데이터는 공유되지 않는다. 각자 컴퓨터에만 남는다.)

---

## 코드 읽어 보기

### 편한 단축키

VS Code 기준이다.

| 키 | 하는 일 |
|---|---|
| `F12` | 커서를 올려 둔 함수가 **어디에 정의돼 있는지** 이동 |
| `Alt` + `←` | 방금 있던 자리로 돌아오기 |
| `Shift` + `F12` | 이 함수를 **쓰는 곳 전부** 찾기 |
| `Ctrl` + `Shift` + `F` | 프로젝트 전체에서 글자 검색 |

`F12` 를 계속 누르면서 따라가면, 명령어 하나가 결국 모터에 신호를 보내는 데까지 내려갈 수 있다. 한 번 해보면 구조가 잡힌다.

### 값을 직접 찍어 보기

문서를 읽는 것보다 **실제 값을 출력해 보는 게 빠를 때가 많다.**

`third_party/lerobot/` 의 파일에 이렇게 한 줄 넣고 명령을 실행하면 된다.

```python
print("여기 값:", action)
```

`.venv` 안에 사본이 있는 게 아니라 **이 파일이 그대로 실행되기 때문에**, 고치면 바로 반영된다.

### 다 보고 나면 되돌리기

```powershell
git diff third_party/          # 내가 뭘 건드렸는지 보기
git checkout -- third_party/   # 전부 원래대로
```

`third_party/` 는 어차피 보호돼 있어서 실수로 올라가지 않지만, 정리해 두는 편이 좋다.

---

## 다음

- [1_setup.md](1_setup.md) — 설치
- [3_commands.md](3_commands.md) — uv 명령어, 환경 점검
- `projects/` — 로봇을 실제로 움직여 보기
