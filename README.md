# SO-101 Project

동아리 로봇팔(SO-101) 프로젝트. 로봇을 움직이고, 데이터를 모으고, 인공지능을 학습시켜 스스로 움직이게 만든다.

`git clone` 하고 `uv sync` 하면 바로 시작할 수 있다.

---

## 빠른 시작

```powershell
git clone https://github.com/<동아리-깃허브-이름>/so101_project.git
cd so101_project
uv sync
```

`uv` 가 없거나 처음이라면 → **[docs/1_setup.md](docs/1_setup.md)** 부터 읽을 것. 20분이면 끝난다.

로봇팔이 없어도 된다. 설치와 코드 읽기는 어떤 컴퓨터에서나 가능하다.

---

## 문서

| 문서 | 내용 |
|---|---|
| [docs/1_setup.md](docs/1_setup.md) | **처음이면 여기부터.** 설치, 그래픽카드 설정 |
| [docs/2_codebase.md](docs/2_codebase.md) | 프로젝트 구조 — 뭐가 어디 있고 누가 고칠 수 있나 |
| [docs/3_commands.md](docs/3_commands.md) | `uv` 사용법, 환경 점검 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | **작업 규칙.** 브랜치, PR 3단계 |
| [projects/](projects/) | 프로젝트 목록 |

로봇을 실제로 움직이는 방법은 `projects/` 의 기초 학습 프로젝트에 있다.

---

## 폴더

```
so101_project/
│
├─ projects/         ★ 작업 구역. 여기는 자유
│
├─ third_party/      lerobot 코드 (빌려 온 것. 읽기만)
├─ calibration/      로봇팔 기준값
├─ docs/             문서
├─ tools/            관리용 도구
│
├─ pyproject.toml    필요한 패키지 목록
└─ uv.lock           그 패키지들의 정확한 버전
```

**`projects/` 안은 자유롭게 작업한다.** 나머지는 메인테이너가 관리하며, 수정하려면 PR 승인이 필요하다.

자세한 설명은 [docs/2_codebase.md](docs/2_codebase.md) 에 있다.

---

## 작업하는 법

> `<...>` 로 감싼 부분은 **자기 값으로 바꿔 쓰는 자리**다. 꺾쇠까지 지우고 쓴다.
>
> | 자리 | 무엇을 넣나 |
> |---|---|
> | `<번호>` | `projects/` 의 다음 순번. 두 자리로 (`03`) |
> | `<주제>` | 프로젝트를 나타내는 영어 소문자. 띄어쓰기는 하이픈 (`hand-tracking`) |
> | `<깃허브-아이디>` | 내 GitHub 계정 이름 |

```powershell
# 1. 양식 복사해서 프로젝트 폴더 만들기
Copy-Item -Recurse projects\_TEMPLATE projects\<번호>-<주제>

# 2. 브랜치 만들기
git checkout master
git pull
git checkout -b feat/<깃허브-아이디>/<주제>

# 3. 작업하고 커밋
git add .
git commit -m "<무엇을 했는지 한 줄>"
git push -u origin feat/<깃허브-아이디>/<주제>
```

<details>
<summary>실제로 채우면 이렇게 된다</summary>

`jsjin7371` 이 손 추적 프로젝트를 세 번째로 만드는 경우:

```powershell
Copy-Item -Recurse projects\_TEMPLATE projects\03-hand-tracking

git checkout master
git pull
git checkout -b feat/jsjin7371/hand-tracking

git add .
git commit -m "손 관절 좌표 추출 추가"
git push -u origin feat/jsjin7371/hand-tracking
```
</details>

완성되면 `master` 로 PR 을 연다. **3단계를 통과해야 머지된다.**

| | 단계 | 누가 |
|---|---|---|
| ① | 코드와 문서 검토 | AI + 메인테이너 |
| ② | 다른 컴퓨터에서 재현 | 누구든 |
| ③ | 세미나 발표 | 작성자 |

코드가 돌아가는지만 보는 게 아니다. 이 프로젝트가 PR 에서 확인하는 것은 하나다.

> **"이 폴더를 처음 보는 사람이, 이것만 읽고 따라 할 수 있는가?"**

동아리 자산으로 남기는 게 목적이라, **가르칠 수 있는 상태인지**를 본다.

자세한 건 [CONTRIBUTING.md](CONTRIBUTING.md) 참고.

---

## 이 리포가 lerobot 과 맺는 관계

로봇 제어에는 [lerobot](https://github.com/huggingface/lerobot) 을 쓴다. 보통은 패키지로 설치해서 쓰지만, **우리는 코드를 `third_party/lerobot/` 안에 복사해 두었다.** 부원들이 직접 열어 보면서 공부하라는 뜻이다.

버전은 특정 시점으로 고정돼 있고, 메인테이너가 확인한 뒤에만 올린다. 현재 버전은 [third_party/UPSTREAM.md](third_party/UPSTREAM.md) 에 적혀 있다.

lerobot 은 Apache-2.0 라이선스다. 원본 라이선스 전문은 [third_party/LICENSE](third_party/LICENSE) 에 있다.

---

## 하드웨어

| | |
|---|---|
| 로봇팔 | SO-101 (follower + leader) |
| 모터 | Feetech STS3215 × 6 |
| 카메라 | USB 웹캠 |

관절 구성:

| ID | 관절 |
|---|---|
| 1 | shoulder_pan |
| 2 | shoulder_lift |
| 3 | elbow_flex |
| 4 | wrist_flex |
| 5 | wrist_roll |
| 6 | gripper |
