# 3. 학습 — 내 컴퓨터

> 녹화한 데이터로 ACT 정책 학습하기. 스모크 테스트, 본 학습, 이어서 학습.

**로봇은 필요 없다.** 2번에서 녹화한 데이터만 있으면 된다.

NVIDIA 그래픽카드가 없다면 [4-train-cloud.md](4-train-cloud.md) 로 갈 것.

---

## 학습이란 무엇을 하는 건가

녹화한 데이터에는 **"이 화면일 때 사람은 관절을 이 각도로 움직였다"** 가 수천 장 들어 있다.

학습은 그 짝을 외우는 것이 아니라 **규칙을 찾는** 과정이다. 처음 보는 화면에도 적당한 각도를 내놓을 수 있게 된다.

우리가 쓰는 모델은 **ACT** 다. 카메라 사진과 현재 관절 각도를 받아서, 다음에 갈 관절 각도를 내놓는다.

---

## 시작하기 전에

### 그래픽카드 확인

```powershell
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

`True` 가 나와야 한다. `False` 면 [docs/1_setup.md 3번](../../docs/1_setup.md) 을 먼저 볼 것.

CPU 로도 돌아가긴 하지만 **20배 느리다.** 5시간이면 끝날 것이 며칠이 된다.

### 개발자 모드 확인

**설정 → 시스템 → 개발자용 → 개발자 모드**

꺼져 있으면 몇 시간 학습한 뒤 **첫 저장에서 죽는다.**

```
OSError: [WinError 1314]
```

### 디스크 공간

체크포인트 하나가 약 **600MB** 다. `--save_freq=5000` 으로 10만 스텝을 돌리면 20개, 약 12GB 다.

---

## 스모크 테스트 — 본 학습 전에 반드시

200 스텝만 돌려 본다. **5분이면 끝난다.**

오타나 권한 문제를 여기서 잡는다. 이걸 건너뛰면 세 시간 뒤에 같은 문제를 만난다.

```powershell
uv run lerobot-train `
    --dataset.repo_id=<내-HF-아이디>/<데이터셋-이름> `
    --policy.type=act `
    --policy.device=cuda `
    --policy.push_to_hub=false `
    --accelerator.mixed_precision=bf16 `
    --dataset.return_uint8=true `
    --batch_size=8 `
    --steps=200 `
    --save_freq=200 `
    --log_freq=25 `
    --output_dir=outputs\train\smoke `
    --job_name=smoke
```

> `<내-HF-아이디>/<데이터셋-이름>` 은 2번에서 녹화하며 만든 것이다. 꺾쇠까지 지우고 쓴다.

끝까지 돌고 `outputs\train\smoke\checkpoints\` 에 폴더가 생기면 성공이다.

한 번 확인했으면 지워도 된다.

```powershell
Remove-Item -Recurse -Force outputs\train\smoke
```

---

## 로그 읽는 법

학습이 돌면 `--log_freq` 간격으로 이런 줄이 나온다.

```
step:200  smpl:2K  ep:5  epch:0.06  loss:0.412  grdn:1.203  lr:1.0e-05  step_s:0.194  smp/s:41
```

| 항목 | 뜻 | 볼 것 |
|---|---|---|
| `step` | 지금까지 몇 번 학습했나 | 목표(`--steps`) 까지 얼마나 남았나 |
| `smpl` `ep` | 지금까지 본 데이터 / 에피소드 수 | 참고용 |
| `epch` | 전체 데이터를 몇 바퀴 봤나 | `1.00` 이면 한 바퀴 다 본 것 |
| `loss` | 예측이 정답에서 얼마나 벗어났나 | **줄어들어야 한다.** 가장 중요 |
| `grdn` | 이번에 얼마나 크게 고쳤나 | 튀지 않고 안정적이면 정상 |
| `lr` | 얼마나 조금씩 고칠지 | ACT 는 `1.0e-05` 고정 |
| `step_s` | 한 스텝에 걸린 시간(초) | **전체 시간 계산에 쓴다** |
| `smp/s` | 초당 처리한 데이터 수 | 빠를수록 좋다 |
| `data_s` `updt_s` | 데이터 읽기 / 계산에 쓴 시간 | `data_s` 가 크면 디스크가 병목 |

### 전체 시간 계산

```
step_s 0.194  →  1 ÷ 0.194 = 초당 5.2 스텝
10만 스텝  ÷  5.2  =  약 19,200초  =  5시간 20분
```

스모크 테스트의 `step_s` 만 보면 본 학습이 몇 시간짜리인지 알 수 있다. **이 숫자를 보고 노트북으로 할지 클라우드로 할지 정한다.**

### `loss` 가 안 줄어들면

- 처음 몇백 스텝은 원래 들쭉날쭉하다. 수천 스텝은 지켜볼 것
- 그 뒤에도 그대로면 데이터가 너무 적거나 일관성이 없을 수 있다

---

## 본 학습

```powershell
uv run lerobot-train `
    --dataset.repo_id=<내-HF-아이디>/<데이터셋-이름> `
    --policy.type=act `
    --policy.device=cuda `
    --policy.push_to_hub=false `
    --accelerator.mixed_precision=bf16 `
    --dataset.return_uint8=true `
    --batch_size=8 `
    --steps=100000 `
    --save_freq=5000 `
    --output_dir=outputs\train\<작업-이름> `
    --job_name=<작업-이름>
```

### 옵션 설명

| 옵션 | 무엇 | 바꿔도 되나 |
|---|---|---|
| `--policy.type=act` | 쓸 모델 | 고정 |
| `--policy.device=cuda` | 그래픽카드 사용 | 고정 |
| `--batch_size=8` | 한 번에 몇 장씩 볼지 | 메모리 부족하면 4로 |
| `--steps=100000` | 몇 번 학습할지 | 조절 가능 |
| `--save_freq=5000` | 몇 스텝마다 저장할지 | 디스크 여유 보고 |
| `--accelerator.mixed_precision=bf16` | 계산을 가볍게 해서 빠르게 | 고정 |
| `--dataset.return_uint8=true` | 영상을 원본 그대로 읽기 | 고정 |
| `--policy.push_to_hub=false` | 자동 업로드 끄기 | 올리려면 `true` |

> **`--output_dir` 는 이미 있는 폴더를 쓸 수 없다.** 같은 이름으로 다시 돌리려면 지우거나 다른 이름을 쓴다.

### 결과물

```
outputs\train\<작업-이름>\checkpoints\
├─ 005000\
├─ 010000\
│   ├─ pretrained_model\    ← 추론에 쓰는 것 (약 200MB)
│   └─ training_state\      ← 이어서 학습할 때 쓰는 것 (약 400MB)
├─ ...
└─ last\                    ← 가장 최근 것으로 가는 바로가기
```

**5번(추론)에서 쓰는 것은 `pretrained_model` 폴더**다.

---

## 노트북으로 돌릴 때

몇 시간 동안 계속 돌아간다. 두 가지를 챙긴다.

```powershell
# 절전으로 안 들어가게 (원래대로: 값을 30 등으로)
powercfg /change standby-timeout-ac 0
```

- **전원을 꽂아 둔다.** 배터리로는 성능이 떨어진다
- 발열이 심하면 받침대를 쓰거나 중간에 멈췄다 이어서 한다 (아래 참고)

---

## 이어서 학습

중간에 멈췄거나 스텝을 더 늘리고 싶을 때.

```powershell
uv run lerobot-train `
    --config_path=outputs\train\<작업-이름>\checkpoints\last\pretrained_model\train_config.json `
    --resume=true
```

마지막으로 저장된 체크포인트부터 이어간다. `--save_freq=5000` 이었다면 **최대 5,000 스텝만 잃는다.**

스텝을 늘리려면 뒤에 붙인다.

```powershell
    --steps=200000
```

**뒤에 쓴 옵션이 저장된 설정을 덮어쓴다.**

---

## Hugging Face 에 올리기

학습이 끝난 뒤 체크포인트를 올려 두면 다른 컴퓨터에서 받아 쓸 수 있다.

```powershell
uv run hf upload <내-HF-아이디>/<모델-이름> outputs\train\<작업-이름>\checkpoints --repo-type=model
```

5번(추론)에서 `--policy.path=<내-HF-아이디>/<모델-이름>` 으로 쓰면 된다.

---

## 다음

- [4-train-cloud.md](4-train-cloud.md) — 더 빠르게 돌리고 싶다면
- [5-inference.md](5-inference.md) — 학습한 모델을 로봇에서 실행
