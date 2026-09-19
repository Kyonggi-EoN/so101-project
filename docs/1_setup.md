# 1. 설치

이 문서를 따라 하면 개발 환경이 준비된다. **로봇팔은 아직 필요 없다.** 20분쯤 걸린다.

---

## 먼저 알아둘 것 3가지

프로그래밍이 처음이어도 이 3개만 알면 아래 내용이 이해된다.

| 말 | 뜻 |
|---|---|
| **패키지** | 남이 미리 만들어 둔 코드 묶음. 우리 프로그램이 빌려 쓴다. 카메라를 다루는 패키지, 인공지능을 돌리는 패키지 같은 것들이 따로 있다. |
| **가상환경** | 이 프로젝트 전용 패키지 보관함. 프로젝트마다 필요한 패키지 버전이 달라서, 한곳에 다 넣으면 서로 충돌한다. 그래서 따로 만든다. |
| **uv** | 위 두 가지를 자동으로 관리해 주는 프로그램. 우리가 직접 할 일은 거의 없다. |

이 프로젝트에서 쓰는 패키지는 84개다. 어떤 버전을 쓸지는 이미 정해져 있고, `uv` 가 알아서 그대로 맞춰 준다.

---

## 시작하기 전에 — PowerShell 여는 법

명령어는 전부 **PowerShell** 이라는 검은 창에 입력한다.

1. 윈도우 탐색기로 `so101-project` 폴더에 들어간다
2. 주소창에 `powershell` 이라고 치고 엔터

그 폴더에서 시작하는 PowerShell 창이 열린다. **항상 `so101-project` 폴더에서 명령을 실행해야 한다.** 다른 데서 실행하면 파일을 못 찾는다.

지금 어디 있는지 확인하려면:

```powershell
pwd
```

`C:\...\so101-project` 가 나오면 맞다.

---

## 1. 윈도우 설정 (컴퓨터마다 한 번만)

### 개발자 모드 켜기

**설정 → 시스템 → 개발자용 → 개발자 모드 켜기**

<details>
<summary>왜 필요한가</summary>

인공지능을 학습시키면 결과물을 파일로 저장하는데, 이때 윈도우의 "바로 가기"와 비슷한 기능을 쓴다. 개발자 모드가 꺼져 있으면 윈도우가 이걸 막아서, **몇 시간 학습시킨 뒤 저장하는 순간 프로그램이 죽는다.**

에러 메시지는 `OSError: [WinError 1314]` 로 나온다. 미리 켜두면 겪을 일이 없다.
</details>

### git 설치

**이 리포를 `git clone` 으로 받았다면 이미 깔려 있다.** 확인만 하고 넘어가면 된다.

```powershell
git --version
```

`git version 2.xx.x` 가 나오면 된다. 없다고 나오면 설치한다.

```powershell
winget install --id Git.Git -e
```

설치 후 **PowerShell 창을 닫고 다시 연다.**

### git 에 내 이름 알려주기 (한 번만)

git 은 "누가 이 코드를 고쳤는지" 를 기록한다. 설정하지 않으면 **커밋이 아예 안 된다.**

```powershell
git config --global user.name "<내 이름 또는 깃허브 아이디>"
git config --global user.email "<깃허브에 등록한 이메일>"
```

> 이메일은 **GitHub 계정에 등록한 것과 같아야** 커밋이 내 것으로 인식된다.
> 이메일을 공개하고 싶지 않다면 GitHub 의 Settings → Emails 에서
> `12345678+아이디@users.noreply.github.com` 형태의 주소를 받아 쓰면 된다.

확인:

```powershell
git config --global --list
```

git 명령어를 더 알고 싶다면 → [4_git.md](4_git.md)

### uv 설치

```powershell
winget install --id=astral-sh.uv -e
```

설치가 끝나면 **PowerShell 창을 닫고 다시 연다.** (새 프로그램을 인식시키기 위해서다.)

확인:

```powershell
uv --version
```

`uv 0.11.x` 같은 게 나오면 성공이다.

<details>
<summary>winget 이 없다고 나오면</summary>

아래 명령으로 직접 설치한다.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

역시 창을 닫고 다시 연 뒤 `uv --version` 으로 확인한다.
</details>

> **파이썬은 따로 설치하지 않아도 된다.** `uv` 가 필요한 버전(3.12)을 알아서 받아온다.

### USB 드라이버 — 로봇팔을 연결할 컴퓨터만

로봇팔을 USB 로 꽂고, 작업 표시줄 검색에서 **장치 관리자**를 연다.
**포트(COM & LPT)** 항목에 `COM3`, `COM5` 같은 게 보이면 된다.

아무것도 안 보이면 드라이버가 없는 것이다. 로봇 제어 보드에 달린 칩 이름(`CH340` 또는 `CP210x`)으로 검색해서 드라이버를 설치한다.

### Hugging Face 로그인 — 나중에 해도 된다

학습 데이터와 인공지능 모델을 인터넷에서 주고받을 때 필요하다. 지금은 건너뛰어도 된다.

```powershell
uv run hf auth login
```

---

## 2. 패키지 설치

```powershell
uv sync
```

이 한 줄이 전부다. 실행하면:

1. `so101-project\.venv\` 폴더가 생긴다 — 여기가 이 프로젝트 전용 패키지 보관함이다
2. 파이썬 3.12 를 받아온다 (없으면)
3. 패키지 84개를 정해진 버전대로 설치한다

**첫 실행은 5~10분쯤 걸린다.** 1GB 정도 내려받는다.

### 잘 됐는지 확인

```powershell
uv run lerobot-find-port --help
```

영어 도움말이 주르륵 나오면 성공이다.

> **`.venv` 폴더는 직접 만들거나 열어볼 필요가 없다.** `uv sync` 가 만들고 관리한다.
> 명령 앞에 `uv run` 만 붙이면 그 안의 프로그램이 실행된다.

<details>
<summary>명령이 `lerobot-` 으로 시작하는 이유</summary>

`lerobot` 이라는 단독 명령은 없다. 기능별로 따로 있다.

```
lerobot-find-port      로봇이 연결된 포트 찾기
lerobot-calibrate      로봇 관절 기준 잡기
lerobot-teleoperate    사람이 조종하기
lerobot-record         데이터 녹화
lerobot-train          인공지능 학습
lerobot-rollout        학습한 인공지능으로 로봇 움직이기
```

전체 목록은 [3_commands.md](3_commands.md) 에 있다.
</details>

---

## 3. 그래픽카드 설정 — 필요한 사람만

**아래 중 하나라도 할 거라면 이 단계가 필요하다.**

- 인공지능을 **학습**시킨다
- 학습된 인공지능으로 **로봇을 움직인다**

단순히 코드를 읽거나 사람이 직접 로봇을 조종하는 거라면 **건너뛰어도 된다.**

### 지금 상태 확인

```powershell
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

두 번째 값이 중요하다.

| 나온 결과 | 뜻 |
|---|---|
| `2.11.0+cpu False` | 그래픽카드를 못 쓴다 → 아래를 실행 |
| `2.11.0+cu128 True` | 이미 설정됨 → 넘어가도 된다 |

### 내 그래픽카드가 NVIDIA 가 아니라면

lerobot 이 쓸 수 있는 그래픽카드는 정해져 있다.

| 그래픽카드 | 가능여부 | 어떻게 |
|---|---|---|
| **NVIDIA** (GeForce, RTX 등) | ✅ | 아래 "설정하기" 그대로 |
| **Intel** (Arc, Core Ultra 내장) | △ | 전용 파이토치를 따로 깔아야 한다. 우리는 시험해 본 적 없다 |
| **Apple** (맥 M1/M2/M3) | ✅ | `--policy.device=mps` |
| **AMD Radeon + 윈도우** | ❌ | 아래 참고 |
| **AMD Radeon + 리눅스** | ✅ | ROCm 버전 파이토치를 설치하면 `cuda` 로 잡힌다 |

**NVIDIA 가 아니면 파이토치를 따로 설치해야 한다는 점은 같다.** 기본 설치는 어떤 그래픽카드도 쓰지 않는다.

<details>
<summary>Intel 그래픽카드를 쓰는 경우</summary>

lerobot 코드에는 Intel 지원이 들어 있어서 `--policy.device=xpu` 로 쓸 수 있게 돼 있다.
다만 **전용 파이토치를 따로 설치해야 한다.** [pytorch.org](https://pytorch.org/get-started/locally/) 에서 XPU 를 골라 확인할 것.

동아리에서 아직 시험해 본 적이 없으니, 해보고 되면 알려주면 이 문서에 반영하겠다.
</details>

<details>
<summary>AMD Radeon 을 쓰는 경우 자세히</summary>

**리눅스라면 된다.** AMD 의 ROCm 은 NVIDIA 의 CUDA 를 흉내 내도록 만들어져 있어서, ROCm 버전 파이토치를 깔면 프로그램이 자기가 NVIDIA 를 쓰는 줄 안다. 명령도 `--policy.device=cuda` 그대로 쓰면 된다. 설치 명령은 [pytorch.org](https://pytorch.org/get-started/locally/) 에서 Linux + ROCm 을 골라 확인할 것.

**윈도우는 방법이 마땅치 않다.** 파이토치의 ROCm 버전이 리눅스용만 나오기 때문이다. (상황이 바뀔 수 있으니 위 링크에서 Windows + ROCm 조합이 있는지 한 번 확인해 보는 것은 좋다.)

`torch-directml` 이라는 대안이 있긴 하지만, 우리가 쓰는 인공지능 모델의 연산을 전부 지원하지 않을 가능성이 커서 권하지 않는다.
</details>

### NVIDIA 가 없어도 괜찮다

그래픽카드가 없거나 Radeon + 윈도우라면 이렇게 하면 된다.

| 하려는 것 | 방법 |
|---|---|
| 코드 읽기, 데이터 다루기 | **CPU 로 충분하다.** 아무것도 안 해도 된다 |
| 사람이 직접 로봇 조종 | **CPU 로 충분하다.** 인공지능을 안 쓰기 때문이다 |
| 인공지능 학습 | **Google Colab 이나 AWS** 를 쓴다. 집 컴퓨터보다 빠르다 |


---

### 설정하기

NVIDIA 그래픽카드가 달린 컴퓨터에서만 의미가 있다.

```powershell
uv pip install --force-reinstall torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
```

2.5GB 를 내려받는다. 끝나면 다시 확인:

```powershell
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

`2.11.0+cu128 True NVIDIA GeForce ...` 처럼 카드 이름까지 나오면 성공이다.

### 이걸 안 하면 어떻게 되나

> **프로그램은 그냥 돌아간다. 20배 느려질 뿐이다.**
>
> 에러가 안 나기 때문에 알아채기 어렵다. 5시간이면 끝날 학습이 며칠이 되고,
> 로봇에 인공지능을 돌리면 반응이 느려서 움직임이 끊긴다.
>
> 작은 경고가 한 줄 찍히긴 한다.
> `No accelerated backend detected. Using default cpu, this will be slow.`
> 다른 메시지에 묻혀 지나가기 쉬우니, 위 확인 명령으로 직접 보는 게 확실하다.

<details>
<summary>왜 기본 설치는 그래픽카드를 안 쓰나 / 왜 버전을 고정하나</summary>

**기본이 CPU 인 이유.** 그래픽카드용 패키지는 2.5GB 라 CPU용(200MB)보다 훨씬 크다. 그래픽카드가 없는 부원에게까지 받게 할 이유가 없어서, 필요한 사람만 추가로 설치하게 했다.

**버전 고정 이유.** `torch 2.11.0` / `torchvision 0.26.0` 은 영상을 읽는 패키지(`torchcodec 0.11.1`)와 짝이 맞는 조합이다. 아무 버전이나 깔면 녹화한 영상을 못 읽는다.

`cu128` 은 CUDA 12.8 을 뜻한다. NVIDIA 드라이버가 **570.86 이상**이어야 한다. 낮으면 드라이버를 먼저 업데이트할 것.
</details>

---

## 끝났다

여기까지 하면 환경 준비가 끝난다.

- 로봇을 움직여 보고 싶다면 → `projects/` 의 기초 학습 문서
- 코드가 어떻게 생겼는지 보고 싶다면 → [2_codebase.md](2_codebase.md)
- `uv` 명령어를 더 알고 싶다면 → [3_commands.md](3_commands.md)
