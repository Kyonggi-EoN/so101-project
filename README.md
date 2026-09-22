# SO-101 Project

동아리 로봇팔 프로젝트.

`git clone` → `uv sync` 두 줄이면 준비가 끝난다. **로봇팔이 없어도 설치와 학습은 된다.**

## 프로젝트

<!-- 새 프로젝트가 머지되면 여기에 한 줄 추가 -->

| 제목 | 내용 | 만든 사람 |
|---|---|---|
| | | |

새로 만들려면 → [projects/README.md](projects/README.md)

---

## 시작하기

```powershell
git clone https://github.com/Kyonggi-EoN/so101-project.git
cd so101-project
uv sync
```

처음이거나 막히면 → **[docs/1_setup.md](docs/1_setup.md)** (20분)

---

## 문서

| | |
|---|---|
| [docs/1_setup.md](docs/1_setup.md) | **처음이면 여기부터.** 설치, 그래픽카드 설정 |
| [docs/2_codebase.md](docs/2_codebase.md) | 프로젝트 구조 — 뭐가 어디 있고 누가 고칠 수 있나 |
| [docs/3_commands.md](docs/3_commands.md) | `uv` 사용법, 환경 점검 |
| [docs/4_git.md](docs/4_git.md) | git 이 처음이라면 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | **작업 규칙.** 브랜치, 커밋, PR 3단계 |
| [AGENTS.md](AGENTS.md) | AI 코딩 도구용 지침 |

로봇을 실제로 움직이는 방법은 `projects/` 의 기초 학습 프로젝트에 있다.

---

## 작업하는 법

**`projects/` 안은 자유**, 나머지는 메인테이너가 관리한다.

```powershell
git checkout -b feat/<깃허브-아이디>/<주제>     # 새 프로젝트
git checkout -b docs/<깃허브-아이디>/<주제>     # 문서 수정
```

작업이 끝나면 `master` 로 PR 을 연다. **3단계를 통과해야 머지된다.**

| | 단계 | 누가 |
|---|---|---|
| ① | 코드와 문서 검토 | AI + 메인테이너 |
| ② | 다른 컴퓨터에서 재현 | 누구든 |
| ③ | 세미나 발표 | 작성자 |

코드가 돌아가는지만 보는 게 아니다. 확인하는 건 하나다.

> **"이 폴더를 처음 보는 사람이, 이것만 읽고 따라 할 수 있는가?"**

동아리 자산으로 남기는 게 목적이라 **가르칠 수 있는 상태인지**를 본다.

자세한 건 → [CONTRIBUTING.md](CONTRIBUTING.md)

---

## AI 도구를 쓴다면

작업을 시키기 전에 **[AGENTS.md](AGENTS.md) 를 읽게 한다.**

```
AGENTS.md 를 먼저 읽고 시작해줘!
```

안 읽히면 AI 가 건드리면 안 되는 폴더를 고치거나, 없는 옵션을 지어내거나, 모터에 토크를 거는 명령을 그냥 실행할 수 있다.

**AI 가 쓴 코드도 본인 책임이다.** 3단계가 세미나 발표라, 설명하지 못하면 통과하지 못한다.
