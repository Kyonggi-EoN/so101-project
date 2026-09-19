# 3. 환경 명령어

`uv` 를 쓰는 법과 환경을 점검하는 법. **로봇을 움직이는 명령은 여기 없다** — `projects/` 의 기초 학습 문서를 볼 것.

> 모든 명령은 `so101-project` 폴더에서 실행한다. `pwd` 로 확인할 수 있다.

---

## 자주 쓰는 명령 4개

| 명령 | 하는 일 | 언제 |
|---|---|---|
| `uv sync` | 패키지를 정해진 버전대로 맞춘다 | 처음 받았을 때, `git pull` 한 뒤 |
| `uv run <명령>` | 프로젝트 환경에서 프로그램을 실행한다 | 매번 |
| `uv pip install <패키지>` | 패키지를 임시로 추가한다 | 뭔가 시험해 볼 때 |
| `uv lock` | 패키지 버전 목록을 다시 계산한다 | 메인테이너만 |

---

## `uv run` 을 붙이는 이유

패키지는 `.venv` 라는 프로젝트 전용 보관함에 들어 있다. 그냥 `python` 이라고 치면 컴퓨터에 원래 있던 파이썬이 실행돼서 **패키지를 못 찾는다.**

```powershell
uv run lerobot-find-port      # ← 보관함 안의 프로그램이 실행된다
```

`uv run` 은 세 가지를 알아서 해준다.

1. `.venv` 안의 프로그램을 찾아서 실행
2. `.venv` 가 없으면 만들어 준다
3. 패키지가 정해진 버전과 다르면 **먼저 맞춰 놓고** 실행한다

3번이 실제로 유용하다. 누가 패키지 버전을 바꾼 걸 `git pull` 로 받아 왔는데 `uv sync` 를 깜빡해도, `uv run` 이 알아서 맞춰 준다.

<details>
<summary>매번 uv run 치기 귀찮다면</summary>

보관함을 "켜 두는" 방식도 있다. 터미널을 열 때 한 번만 치면 된다.

```powershell
.\.venv\Scripts\Activate.ps1
```

프롬프트 앞에 `(so101-project)` 가 붙는다. 이제 `uv run` 없이 바로 친다.

```powershell
lerobot-find-port
```

끄려면 `deactivate`. **터미널을 새로 열면 다시 켜야 한다.**

둘 중 아무거나 써도 되고, 섞어 써도 된다. 같은 보관함을 쓴다.
</details>

---

## 환경 점검

설치가 제대로 됐는지 한 번에 확인한다.

```powershell
uv run python -c "import lerobot, torch; print(lerobot.__version__); print(torch.__version__, torch.cuda.is_available())"
```

결과 읽는 법:

| 나온 값 | 뜻 |
|---|---|
| `0.6.2` | lerobot 이 제대로 잡혔다 |
| `2.11.0+cpu  False` | 그래픽카드를 안 쓰는 상태 |
| `2.11.0+cu128  True` | 그래픽카드 사용 가능 |

학습하거나 로봇에 인공지능을 돌릴 컴퓨터인데 `False` 가 나왔다면 [1_setup.md 3번](1_setup.md) 을 볼 것.

### 설치된 명령어 목록 보기

```powershell
Get-ChildItem .venv\Scripts\lerobot-*.exe | Select-Object -ExpandProperty Name
```

19개가 나온다. SO-101 로 쓰는 건 그중 9개다.

---

## 뭔가 꼬였을 때

### 일단 이것부터

```powershell
uv sync
```

대부분 해결된다. 빠진 패키지를 채우고, 버전이 다른 건 맞추고, 목록에 없는 건 지운다.

### 그래도 안 되면 — 보관함 통째로 새로 만들기

```powershell
Remove-Item -Recurse -Force .venv
uv sync
```

`.venv` 는 **언제든 지워도 되는 폴더다.** 우리가 만든 코드가 아니라 `uv` 가 만든 것이고, 다시 만들면 똑같이 복원된다.

지워도 `third_party/lerobot/`, `calibration/`, `projects/` 는 그대로 남는다. 서로 무관하다.

### 명령어 도움말 보기

```powershell
uv run lerobot-teleoperate --help
```

옵션이 너무 많이 나오면, 로봇 종류를 같이 알려 주면 그에 맞는 것만 보여 준다.

```powershell
uv run lerobot-teleoperate --robot.type=so101_follower --help
```

---

## lerobot 버전 올리기 — 메인테이너 전용

> 이 절은 **메인테이너**(이 프로젝트를 관리하고 코드 검토를 맡는 사람, 현재 `@jsjin7371`)만
> 해당된다. 부원은 읽지 않아도 된다.

`third_party/lerobot/` 은 원본을 복사해 온 것이라 손으로 고치지 않는다. 스크립트를 쓴다.

```powershell
.\tools\update_lerobot.ps1 -Rev <업스트림 커밋 해시 40자>
uv lock
uv sync
```

스크립트가 하는 일:

1. 원본 저장소에서 지정한 버전만 받아 온다 (전체 기록을 받지 않아 빠르다)
2. `third_party/lerobot/` 을 통째로 갈아 끼운다
3. **원본의 패키지 목록이 바뀌었으면 그 차이를 보여 준다** — 우리 `pyproject.toml` 에 반영할지 판단한다
4. `third_party/UPSTREAM.md` 에 버전과 날짜를 기록한다

`pyproject.toml` 은 자동으로 고치지 않는다. 우리가 바꾼 4곳이 파일 맨 위 주석에 적혀 있으니 참고할 것.

**커밋하기 전에 로봇에 연결해서 한 바퀴 확인한다.** 조종 → 짧은 녹화 → 인공지능 실행까지 되면 올려도 된다.

문제가 생기면 이전 버전으로 돌리면 된다.

```powershell
.\tools\update_lerobot.ps1 -Rev <이전 해시>
```

현재 버전은 [../third_party/UPSTREAM.md](../third_party/UPSTREAM.md) 에 있다.

---

## 다음

- [1_setup.md](1_setup.md) — 설치
- [2_codebase.md](2_codebase.md) — 프로젝트 구조
- `projects/` — 로봇을 실제로 움직여 보기
- [4_git.md](4_git.md) — git 이 처음이라면
