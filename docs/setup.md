# 설치

처음 오면 이 문서만 따라가면 된다. 로봇팔이 없어도 6번까지 가능하다.

> 모든 명령은 **리포 루트**(`so101_project\`)에서 실행한다.
> 학습 출력이 상대경로(`outputs/train/...`)라 실행 위치가 중요하다.

---

## 1. 1회성 Windows 설정

로봇을 처음 쓰는 컴퓨터에서 한 번만 하면 된다. 건너뛰면 나중에 엉뚱한 곳에서 막힌다.

### 개발자 모드 켜기

설정 → 시스템 → 개발자용 → **개발자 모드 켜기**

체크포인트를 저장할 때 심볼릭 링크를 만드는데, 꺼져 있으면 학습이 `OSError: [WinError 1314]` 로 죽는다. 몇 시간 돌린 뒤 첫 저장에서 죽으므로 미리 켜둘 것.

### USB 시리얼 드라이버

SO-101 컨트롤 보드를 꽂고 장치 관리자에서 `COM` 포트가 보이는지 확인한다.
안 보이면 보드에 달린 USB-시리얼 칩(CH340 또는 CP210x) 드라이버를 설치한다.

### uv 설치

```powershell
winget install --id=astral-sh.uv -e
```

파이썬은 따로 안 깔아도 된다. `uv` 가 3.12 를 알아서 받아온다.

### Hugging Face 로그인

데이터셋과 체크포인트를 주고받는 데 필요하다. 로봇만 움직일 거면 나중에 해도 된다.

```powershell
uv run hf auth login
```

---

## 2. 리포 받기

```powershell
git clone https://github.com/<조직>/so101_project.git
cd so101_project
```

---

## 3. 설치

```powershell
uv sync
```

`.venv\` 가 생기고 패키지 84개가 깔린다. 첫 실행은 몇 분 걸린다.

확인:

```powershell
uv run lerobot-find-port --help
```

도움말이 뜨면 성공이다.

> **`.venv` 를 직접 만들거나 활성화할 필요 없다.** `uv sync` 가 만들고, 명령 앞에 `uv run` 을 붙이면 알아서 그 환경을 쓴다.

---

## 4. GPU 설정 — 학습하거나 로봇에 추론을 돌릴 PC만

`uv sync` 는 **CPU 빌드 torch** 를 설치한다. GPU 없는 부원에게 2.5GB 를 받게 하지 않기 위한 선택이다.

```powershell
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

`2.11.0+cpu False` 가 나오는데 이 PC 로 **학습하거나 로봇에 정책을 돌릴 거라면** 아래를 실행한다.

```powershell
uv pip install --force-reinstall torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

`2.11.0+cu128 True NVIDIA ...` 가 나와야 한다. NVIDIA 드라이버 570.86 이상이 필요하다.

> **왜 중요한가.** CPU 빌드로도 프로그램은 돌아간다. 그냥 20배 느려질 뿐이다.
> 학습은 5시간이 며칠이 되고, `lerobot-rollout` 은 추론이 느려서 30Hz 제어 주기를 못 맞춘다.
> 경고가 한 줄 찍히지만(`No accelerated backend detected. Using default cpu, this will be slow.`)
> 다른 로그에 섞여 지나가기 쉬우니 위 명령으로 직접 확인할 것.

버전을 `2.11.0` / `0.26.0` 으로 고정하는 이유는 `torchcodec 0.11.1` 과 맞는 짝이기 때문이다. 이걸 깨면 영상 디코딩이 안 된다.

---

## 5. 포트와 카메라 번호 찾기

### 포트

```powershell
uv run lerobot-find-port
```

USB 를 뽑았다 꽂으라고 안내한다. leader 와 follower 각각 실행해서 두 개를 알아낸다.

COM 번호는 **USB 슬롯을 바꾸면 달라진다.** 안 되면 다시 확인할 것.

```powershell
Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'COM\d+' } | Select-Object -ExpandProperty Name
```

### 카메라

```powershell
uv run lerobot-find-cameras opencv
```

각 카메라에서 한 장씩 찍어 `outputs\captured_images\` 에 저장한다. 이미지를 열어보면 어느 번호가 어느 카메라인지 바로 안다.

- 노트북 내장 웹캠이 있으면 보통 0번을 가져간다
- 재부팅하면 번호가 바뀔 수 있다
- 지원하지 않는 해상도/fps 를 주면 **조용히 다른 값으로 열린다.** 위 명령 로그에 찍힌 실제 지원값을 쓸 것

---

## 6. `local.ps1` 만들기

머신마다 다른 값이라 git 에 올리지 않는다(`.gitignore` 에 있음). 리포 루트에 직접 만든다.

```powershell
# local.ps1  — 내 컴퓨터 전용 설정
$PORT_FOLLOWER = "COM6"        # 5번에서 찾은 값
$PORT_LEADER   = "COM5"
$CAM_TOP       = 0             # 카메라 번호

# 캘리브레이션을 리포 안에서 찾게 한다. 이게 있으면 명령마다 경로를 안 써도 된다.
$env:HF_LEROBOT_CALIBRATION = "$PSScriptRoot\calibration"
```

터미널을 열 때마다 한 번 불러온다.

```powershell
. .\local.ps1
```

> 앞에 **점과 공백**(`. .\`)이 있어야 한다. 그냥 `.\local.ps1` 로 실행하면 변수가 자식 프로세스에만 설정되고 사라진다.

---

## 7. 동작 확인

팔 두 개를 연결하고 leader 를 움직였을 때 follower 가 따라오면 끝이다.

```powershell
. .\local.ps1

uv run lerobot-teleoperate `
    --robot.type=so101_follower --robot.port=$PORT_FOLLOWER --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --teleop.type=so101_leader --teleop.port=$PORT_LEADER --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader `
    --fps=30 --display_data=false
```

**캘리브레이션은 하지 않아도 된다.** 값이 리포에 들어 있다.

만약 관절을 손으로 돌리라는 안내가 나오면 무언가 잘못된 것이다. 임의로 진행하지 말고 [commands.md 의 캘리브레이션 절](commands.md#3-캘리브레이션) 을 먼저 읽을 것.

---

## 다음

- [commands.md](commands.md) — 녹화·학습·추론 명령어
- [codebase.md](codebase.md) — lerobot 코드 구조
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — 작업 규칙
