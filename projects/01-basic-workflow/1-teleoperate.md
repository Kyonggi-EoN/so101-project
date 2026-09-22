# 1. 연결과 조종

> 포트·카메라 찾기, 캘리브레이션, leader 로 follower 움직이기.

<!--
작성할 때 이 순서를 지킬 것.

  1. 로봇 연결 확인 (장치 관리자에 COM 포트가 보이는지)
  2. uv run lerobot-find-port             → 포트 2개. 팔마다 한 번씩
  3. uv run lerobot-find-cameras opencv   → 카메라 번호
  4. 모터 등록과 캘리브레이션 — 개념만. 건너뛴다는 것까지 (작성됨)
  5. uv run lerobot-teleoperate           → leader 를 움직이면 follower 가 따라온다 (작성됨)

[주의] 명령에 쓰는 COM 포트와 카메라 번호는 컴퓨터마다 다르다.
       예시 값을 그대로 두지 말고, 명령마다 아래처럼 표시할 것.

         --robot.port=COM6      ← lerobot-find-port 로 찾은 자기 포트로 바꿀 것

[주의] 캘리브레이션 경로는 명령에 직접 쓴다. 업스트림이 폴더 이름을 바꿔도 안 깨진다.

         --robot.calibration_dir=calibration/robots/so_follower
         --teleop.calibration_dir=calibration/teleoperators/so_leader
-->

> ### 📸 캡처 넣을 자리 — 카메라 번호 확인
>
> `images/find-cameras-output.png` 로 저장한다.
>
> - `lerobot-find-cameras opencv` 실행 후 `outputs\captured_images\` 를 연다
> - 여러 이미지가 **번호와 함께 보이게** 탐색기 창을 캡처
> - 어느 번호가 로봇 카메라인지 고르는 방법을 보여주는 것이 목적
>
> 저장한 뒤 아래 줄의 `<!--` 와 `-->` 를 지워서 살린다.

<!-- ![lerobot-find-cameras 가 저장한 이미지들](images/find-cameras-output.png) -->

---

## 모터 등록과 캘리브레이션

<!--
[작성 가이드]

아래 세 가지를 각각 두세 줄로만 쓴다. 신입에게 깊이 설명할 주제가 아니다.
"이런 게 있는데 우리는 안 해도 된다" 를 알려주는 것이 목적이다.

  (1) 모터 등록(ID 굽기)이 무엇인가
      - 모터 6개가 한 선에 물려 있어서 번호로 구분한다는 것
      - 출하 상태는 전부 1번이라 그대로 쓰면 충돌한다는 것
      - 명령: lerobot-setup-motors

  (2) 캘리브레이션이 무엇인가
      - 각 관절의 "0도" 와 움직일 수 있는 범위를 정하는 작업
      - 이 기준이 달라지면 같은 명령에도 다른 자세가 나온다는 것
      - 명령: lerobot-calibrate

  (3) 원래는 어떻게 하는가
      - 모터를 하나씩 연결하며 번호를 굽고, 관절을 끝에서 끝까지 손으로 돌린다
      - 절차를 자세히 쓰지 말 것. 아래 "건너뛴다" 가 핵심이다

아래 두 절은 작성 완료. 손대지 않아도 된다.
-->

### 우리는 건너뛴다

**동아리 팔은 둘 다 이미 되어 있다.** 새로 할 필요가 없다.

- **모터 등록** — 팔을 조립할 때 한 번 구웠고, 번호는 모터 안에 저장돼 있다
- **캘리브레이션** — 기준값이 서보 안에 저장돼 있고, 같은 값이 `calibration/` 에도 커밋돼 있다

그래서 컴퓨터를 바꿔도 로봇은 자기 설정을 기억한다. 연결할 때 lerobot 이 모터에서 값을 읽어 `calibration/` 의 파일과 대조하고, 같으면 그냥 넘어간다.

명령에 아래 두 줄만 붙이면 된다.

```powershell
--robot.calibration_dir=calibration/robots/so_follower `
--teleop.calibration_dir=calibration/teleoperators/so_leader
```

### 이럴 때는 필요하다 — 메인테이너가 진행한다

연결할 때 이런 메시지가 나오면 어긋난 것이다.

```
Mismatch between calibration values in the motor and the calibration file
or no calibration file found
```

| 원인 | 어떻게 |
|---|---|
| 위 두 줄을 빼먹었다 | 명령을 다시 확인한다. 대부분 이것이다 |
| 모터를 교체했다 | 캘리브레이션이 실제로 필요하다 |
| 다른 팔이다 | `--robot.id` 를 그 팔 이름으로 바꾼다 |

> **직접 캘리브레이션하지 말 것.**
> 기준값을 새로 잡으면 이미 녹화한 데이터, 학습된 모델과 전부 어긋난다.
> 위 메시지가 나오면 메인테이너에게 알린다.

---

## 조종하기

leader 팔을 손으로 움직이면 follower 팔이 따라온다.

```powershell
uv run lerobot-teleoperate `
    --robot.type=so101_follower --robot.port=COM6 --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --teleop.type=so101_leader --teleop.port=COM5 --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader `
    --robot.cameras="{ top: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30} }" `
    --fps=30 `
    --display_data=true
```

> **`COM6` · `COM5` · `index_or_path: 0` 은 예시 값이다.**
> 위에서 `lerobot-find-port` · `lerobot-find-cameras` 로 찾은 자기 값으로 바꿀 것.

> ### ⚠ `calibration_dir` 두 줄은 절대 빼지 말 것
>
> 이 줄이 없으면 lerobot 이 관절 기준값을 못 찾고 **묻지도 않고 캘리브레이션을 시작한다.**
> "관절을 중간으로 옮기고 ENTER" 같은 안내가 나오는데, 시키는 대로 따라 하면
> **로봇 안에 저장된 기준값이 덮어써진다.**
>
> 그러면 지금까지 녹화한 데이터도, 학습해 둔 모델도 전부 안 맞게 된다.
> 팔은 동아리에 한 대뿐이다.

줄 끝의 백틱(`` ` ``)은 **명령이 다음 줄로 이어진다**는 뜻이다. 뒤에 공백이 있으면 안 된다.

### 옵션 설명

| 옵션 | 무엇 |
|---|---|
| `--robot.*` | 움직이는 쪽 팔 (follower) |
| `--teleop.*` | 사람이 잡는 쪽 팔 (leader) |
| `--*.calibration_dir` | 관절 기준값 위치. 빼면 안 된다 |
| `--robot.cameras` | 카메라 설정. 없으면 통째로 빼도 된다 |
| `--fps=30` | 초당 몇 번 돌릴지 |
| `--display_data=true` | 화면에 그려서 보여준다 |

**`--fps=30` 은 꼭 쓴다.** 기본값이 60인데 카메라가 30fps 라 못 따라가고 경고가 쏟아진다.

### 무엇을 보게 되나

`--display_data=true` 를 켜면 **rerun** 이라는 창이 뜬다.

> ### 📸 캡처 넣을 자리
>
> rerun 창이 떠 있는 화면을 캡처해서 `images/rerun-teleoperate.png` 로 저장한다.
>
> - `--display_data=true` 로 teleoperate 실행
> - **leader 를 움직여 관절 그래프가 반응하는 순간**을 캡처 (정지 화면보다 이해가 빠르다)
> - 카메라 화면과 관절 그래프가 **둘 다 보이게** 창 크기를 맞출 것
>
> 저장한 뒤 아래 줄의 `<!--` 와 `-->` 를 지워서 살린다.

<!-- ![rerun 화면 — 카메라 영상과 관절 6개의 각도 그래프](images/rerun-teleoperate.png) -->

거기서 볼 수 있는 것:

- 카메라 화면
- 관절 6개의 각도가 실시간으로 변하는 그래프
- leader 가 보낸 값과 follower 의 현재 값

leader 를 움직여 보면 그래프가 따라 움직인다.

다만 화면을 그리느라 제어 루프가 느려진다. **구조를 눈으로 익힐 때만 켜고, 녹화할 때는 끄는 것을 추천한다**(`--display_data=false`).

### 끝내기

터미널에서 `Ctrl + C`.
