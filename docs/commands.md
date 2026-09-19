# 명령어

설치는 [setup.md](setup.md) 를 먼저 볼 것.

## 공통

모든 명령은 **리포 루트**에서, 터미널을 열 때 한 번 `local.ps1` 을 불러온 뒤 실행한다.

```powershell
cd C:\...\so101_project
. .\local.ps1
```

| 변수 | 내용 |
|---|---|
| `$PORT_FOLLOWER` | follower 팔의 COM 포트 |
| `$PORT_LEADER` | leader 팔의 COM 포트 |
| `$CAM_TOP` | 카메라 번호 |

명령이 길어서 PowerShell 줄바꿈 문자 **백틱(`` ` ``)** 을 쓴다. 백틱 뒤에 공백이 있으면 안 된다.

### 관절 ID

| ID | 관절 |
|---|---|
| 1 | shoulder_pan |
| 2 | shoulder_lift |
| 3 | elbow_flex |
| 4 | wrist_flex |
| 5 | wrist_roll |
| 6 | gripper |

---

## 1. 장치 확인

```powershell
uv run lerobot-find-port           # COM 포트 찾기
uv run lerobot-find-cameras opencv # 카메라 번호 찾기 → outputs\captured_images\
```

---

## 2. 모터 ID 굽기

팔을 새로 조립했거나 모터를 교체했을 때만 한다. 모터는 각자 버스 위에서 자기 ID 로 응답하는데, 출하 상태는 보통 전부 ID=1 이라 그대로 연결하면 충돌한다.

```powershell
uv run lerobot-setup-motors --robot.type=so101_follower --robot.port=$PORT_FOLLOWER
```

안내에 따라 모터를 하나씩 연결하면서 1번부터 6번까지 순서대로 굽는다.

> 모터를 굽고 나면 **캘리브레이션을 다시 해야 한다.** 다음 절을 읽을 것.

---

## 3. 캘리브레이션

> ### 함부로 실행하지 말 것
>
> 캘리브레이션 값(`homing_offset`)은 **엔코더 원시값 ↔ 각도** 의 변환 기준이다.
> 녹화된 데이터셋의 관절 각도도, 학습된 정책이 출력하는 각도도 전부 이 기준으로 기록돼 있다.
> 새로 잡으면 기준이 바뀌어서 **같은 체크포인트가 다른 자세로 움직인다.**
>
> 현재 값은 `calibration/` 에 커밋돼 있고 명령들이 자동으로 참조한다. **평소에는 실행할 일이 없다.**

### 다시 해야 하는 경우

**모터를 교체했을 때뿐이다.** 서보 EEPROM 에도 같은 값이 들어 있어서, 새 모터는 기존 파일과 맞지 않는다. lerobot 이 감지해서 알려준다.

```
Mismatch between calibration values in the motor and the calibration file
or no calibration file found
```

이 메시지가 모터를 안 바꿨는데 떴다면 **경로 문제다.** `local.ps1` 을 불러왔는지, 명령에 `--robot.calibration_dir` 이 있는지 먼저 확인할 것. 캘리브레이션을 새로 하면 안 된다.

### 실행

```powershell
uv run lerobot-calibrate `
    --robot.type=so101_follower --robot.port=$PORT_FOLLOWER --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower

uv run lerobot-calibrate `
    --teleop.type=so101_leader --teleop.port=$PORT_LEADER --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader
```

**끝나면 바뀐 JSON 을 반드시 커밋한다.** 안 하면 다음 사람이 또 캘리브레이션하게 된다.

---

## 4. 텔레오퍼레이션

leader 를 손으로 움직이면 follower 가 따라온다.

```powershell
uv run lerobot-teleoperate `
    --robot.type=so101_follower --robot.port=$PORT_FOLLOWER --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --teleop.type=so101_leader --teleop.port=$PORT_LEADER --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader `
    --robot.cameras="{ top: {type: opencv, index_or_path: $CAM_TOP, width: 640, height: 480, fps: 30} }" `
    --fps=30 `
    --display_data=false
```

- `--fps=30` 을 **카메라 fps 에 맞춰 명시한다.** 기본값이 60 이라 안 쓰면 제어 루프가 못 따라가고 경고가 쏟아진다
- `--display_data=true` 를 켜면 rerun 으로 화면을 볼 수 있다. 다만 제어 루프가 느려진다
- 카메라 없이 팔만 움직여볼 거면 `--robot.cameras` 를 빼면 된다

---

## 5. 녹화

```powershell
uv run lerobot-record `
    --robot.type=so101_follower --robot.port=$PORT_FOLLOWER --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --teleop.type=so101_leader --teleop.port=$PORT_LEADER --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader `
    --robot.cameras="{ top: {type: opencv, index_or_path: $CAM_TOP, width: 640, height: 480, fps: 30} }" `
    --dataset.repo_id=<HF_아이디>/<데이터셋_이름> `
    --dataset.single_task="Pick up the block" `
    --dataset.num_episodes=40 `
    --dataset.episode_time_s=40 `
    --dataset.reset_time_s=20 `
    --display_data=false
```

녹화 중 키:

| 키 | 동작 |
|---|---|
| `→` 또는 `n` | 현재 에피소드 끝내고 다음으로 |
| `←` 또는 `r` | 현재 에피소드 다시 녹화 |
| `Esc` 또는 `q` | 녹화 종료 |

- **끝나면 Hugging Face 에 자동 업로드된다.** 끄려면 `--dataset.push_to_hub=false`
- `repo_id` 뒤에 날짜·시각이 자동으로 붙는다 → `<이름>_20260831_175644`.
  끄려면 `--dataset.no_stamp=true` (같은 이름에 이어 붙이고 싶을 때)
- 로컬 저장 위치는 `C:\Users\<사용자>\.cache\huggingface\lerobot\<HF_아이디>\`
- 키가 안 먹히면 VS Code 내장 터미널 대신 **일반 PowerShell 창**에서 실행할 것

내 데이터셋 목록 보기:

```powershell
uv run python -c "from huggingface_hub import HfApi; [print(d.id) for d in HfApi().list_datasets(author='<HF_아이디>')]"
```

---

## 6. 재생

녹화한 궤적을 사람 입력 없이 그대로 재생한다. follower 만 있으면 된다.

```powershell
uv run lerobot-replay `
    --robot.type=so101_follower --robot.port=$PORT_FOLLOWER --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --dataset.repo_id=<HF_아이디>/<데이터셋_이름> `
    --dataset.episode=0
```

---

## 7. 학습

로봇이 필요 없다. GPU 설정([setup.md 4절](setup.md#4-gpu-설정--학습하거나-로봇에-추론을-돌릴-pc만))을 먼저 할 것.

### 스모크 테스트 — 본 학습 전에 반드시

200 스텝만 돌려서 옵션 오타나 권한 문제를 미리 잡는다. 5분이면 끝난다.

```powershell
uv run lerobot-train `
    --dataset.repo_id=<HF_아이디>/<데이터셋_이름> `
    --policy.type=act --policy.device=cuda --policy.push_to_hub=false `
    --accelerator.mixed_precision=bf16 --dataset.return_uint8=true `
    --batch_size=8 --steps=200 --save_freq=200 --log_freq=25 `
    --output_dir=outputs\train\smoke --job_name=smoke
```

로그의 `step_s` 로 전체 시간을 계산한다. 예: `0.194` → 5.2 step/s → 10만 스텝 약 5시간 20분.

### 본 학습

```powershell
uv run lerobot-train `
    --dataset.repo_id=<HF_아이디>/<데이터셋_이름> `
    --policy.type=act `
    --policy.device=cuda `
    --policy.push_to_hub=false `
    --accelerator.mixed_precision=bf16 `
    --dataset.return_uint8=true `
    --batch_size=8 `
    --steps=100000 `
    --save_freq=5000 `
    --output_dir=outputs\train\<작업이름> `
    --job_name=<작업이름>
```

- `--save_freq` 간격으로 체크포인트가 저장된다. 하나에 약 600MB 라 디스크를 확인할 것
- `outputs\` 는 `.gitignore` 에 있다. 커밋되지 않는다

### 이어서 학습

중단됐거나 스텝을 더 늘리고 싶을 때.

```powershell
uv run lerobot-train `
    --config_path=outputs\train\<작업이름>\checkpoints\last\pretrained_model\train_config.json `
    --resume=true
```

`--config_path` 뒤에 다른 옵션을 붙이면 **저장된 설정을 덮어쓴다.** 예를 들어 `--steps=200000` 을 추가하면 목표 스텝이 늘어난다.

---

## 8. 추론 (로봇에서 정책 실행)

follower 만 연결하면 된다. leader 는 필요 없다.

```powershell
uv run lerobot-rollout `
    --strategy.type=base `
    --policy.path=<HF_아이디>/<모델_이름> `
    --policy.pretrained_revision=100000 `
    --policy.device=cuda `
    --robot.type=so101_follower --robot.port=$PORT_FOLLOWER --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --robot.cameras="{ top: {type: opencv, index_or_path: $CAM_TOP, width: 640, height: 480, fps: 30} }" `
    --task="Pick up the block" `
    --fps=30 `
    --duration=10
```

> ### 처음 돌릴 때
>
> - **`--duration` 을 반드시 짧게 준다.** 기본값 0 은 무한이라 `Ctrl+C` 를 누를 때까지 움직인다
> - 손을 전원 스위치 근처에 두고 시작할 것
> - 카메라 위치와 조명이 녹화할 때와 다르면 엉뚱하게 움직인다

- `--policy.pretrained_revision` — 쓸 체크포인트 스텝 (`030000`, `060000`, `100000` …)
- 로컬 체크포인트: `--policy.path=outputs\train\<작업이름>\checkpoints\020000\pretrained_model`
- `--interactive=true` 를 붙이면 `/start`, `/stop` 으로 모델을 다시 로딩하지 않고 반복 실행할 수 있다

Hub 에 올라간 체크포인트 목록:

```powershell
uv run python -c "from huggingface_hub import HfApi; print(sorted({f.split('/')[1] for f in HfApi().list_repo_files('<HF_아이디>/<모델_이름>') if f.startswith('checkpoints/')}))"
```

---

## 9. 도움말 보는 법

옵션은 코드의 dataclass 에서 자동 생성된다. `--help` 를 두 번 쳐보면 구조가 보인다.

```powershell
uv run lerobot-teleoperate --help                              # 최상위 옵션
uv run lerobot-teleoperate --robot.type=so101_follower --help  # SO-101 전용 옵션
```

왜 이렇게 되는지는 [codebase.md](codebase.md#cli-인자가-처리되는-방식) 참고.
