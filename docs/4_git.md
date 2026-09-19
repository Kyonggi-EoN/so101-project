# 4. git 기초

git 을 처음 쓰는 사람을 위한 문서. 설치와 최초 설정은 [1_setup.md](1_setup.md) 에 있다.

이 프로젝트의 작업 규칙(브랜치 이름, PR 3단계)은 [../CONTRIBUTING.md](../CONTRIBUTING.md) 에 있다.

---

## git 이 뭘 하는 건가

**코드의 저장 기록을 남기는 도구**다. 게임의 세이브 파일과 비슷하다.

- 언제든 이전 상태로 되돌릴 수 있다
- 누가 무엇을 왜 고쳤는지 남는다
- 여러 사람이 같은 코드를 동시에 고쳐도 합칠 수 있다

**GitHub** 은 그 기록을 인터넷에 올려 두는 곳이다. git 과 GitHub 은 다른 것이다 — git 은 내 컴퓨터에서 도는 프로그램이고, GitHub 은 웹사이트다.

---

## 세 개의 공간

git 을 이해하려면 이 그림 하나면 된다.

```
내 폴더          →   준비 구역        →   저장 기록       →   GitHub
(파일 수정)          (git add)           (git commit)        (git push)
```

| 공간 | 무엇 |
|---|---|
| **내 폴더** | 지금 파일을 고치고 있는 상태 |
| **준비 구역** | "이번에 기록할 것" 으로 골라 둔 파일들 |
| **저장 기록** | 실제로 기록된 시점들. 여기로 돌아올 수 있다 |
| **GitHub** | 인터넷에 올려 둔 사본. 다른 사람도 볼 수 있다 |

파일을 고쳤다고 자동으로 기록되지 않는다. **내가 직접 골라서(`add`) 기록해야(`commit`) 한다.**

---

## 매일 쓰는 명령 5개

이 다섯 개면 대부분 된다.

```powershell
git status      # 지금 뭐가 바뀌었나
git add .       # 바뀐 것 전부 준비 구역으로
git commit -m "<한 줄 설명>"    # 기록하기
git push        # GitHub 에 올리기
git pull        # GitHub 에서 최신 내용 받기
```

### `git status` — 가장 자주 쓴다

뭘 하기 전에 일단 쳐 본다.

```powershell
git status
```

```
On branch feat/jsjin7371/hand-tracking
Changes not staged for commit:
        modified:   projects/03-hand-tracking/main.py     ← 고쳤지만 준비 안 됨
Untracked files:
        projects/03-hand-tracking/README.md               ← git 이 모르는 새 파일
```

| 영어 | 뜻 |
|---|---|
| `modified` | 고쳤다 |
| `Untracked` | 새로 만든 파일. git 이 아직 모른다 |
| `Changes to be committed` | 준비 구역에 들어갔다 |
| `nothing to commit, working tree clean` | 바뀐 게 없다 |

### `git add` — 기록할 것 고르기

```powershell
git add .                    # 바뀐 것 전부
git add projects/03-hand-tracking/main.py    # 파일 하나만
```

`.` 은 "현재 폴더 전부" 라는 뜻이다. `.gitignore` 에 적힌 것들(학습 결과, 영상 등)은 자동으로 빠진다.

### `git commit` — 기록하기

```powershell
git commit -m "feat: 손 관절 좌표 추출 추가"
```

`-m` 뒤의 메시지는 **무엇을 했는지 알아볼 수 있게** 쓴다. 나중에 "그 기능 언제 넣었지?" 하고 찾을 때 이것만 보인다.

### 앞에 종류를 붙인다

업계에서 널리 쓰는 방식이다. **무엇에 관한 변경인지**를 앞에 한 단어로 적는다.

```
<종류>: <무엇을 했는지>
```

| 종류 | 언제 |
|---|---|
| `feat:` | 새 기능을 추가했을 때 |
| `fix:` | 잘못 동작하던 것을 고쳤을 때 |
| `docs:` | 문서만 고쳤을 때 |
| `refactor:` | 동작은 그대로인데 코드를 정리했을 때 |
| `chore:` | 설정 파일, 패키지 버전 등 잡일 |
| `test:` | 테스트 코드 |

```
feat: 손 관절 좌표 추출 추가
fix: 카메라 인덱스가 바뀌면 죽는 문제 수정
docs: 실행 방법에 준비물 목록 추가
chore: lerobot 버전 업데이트
```

**종류는 영어로, 내용은 한국어로** 쓰면 된다. 헷갈리면 `feat:` 이나 `chore:` 로 두면 무난하다.

### 왜 이렇게 쓰나

기록 목록을 보면 바로 드러난다.

```
docs: 실행 방법에 준비물 목록 추가          ← 문서만 바뀌었구나
fix: 카메라 인덱스가 바뀌면 죽는 문제 수정   ← 버그 고쳤구나
feat: 손 관절 좌표 추출 추가                ← 기능 추가됐구나
수정                                        ← ???
ㅇㅇ                                        ← ???
```

`수정`, `ㅇㅇ`, `update` 같은 메시지는 나중에 찾을 때 아무 도움이 안 된다. 본인이 쓴 것도 일주일 뒤면 기억나지 않는다.

### `git push` — GitHub 에 올리기

```powershell
git push
```

**새 브랜치는 첫 push 때만 다르게 쓴다.**

```powershell
git push -u origin feat/<깃허브-아이디>/<주제>
```

`-u` 는 "이 브랜치는 GitHub 의 저 브랜치와 짝" 이라고 알려 주는 것이다. 한 번 해두면 다음부터는 `git push` 만 하면 된다.

### `git pull` — 최신 내용 받기

```powershell
git pull
```

다른 사람이 올린 것을 내 컴퓨터로 가져온다. **작업을 시작하기 전에 한 번 하는 습관을 들이면** 충돌이 줄어든다.

---

## 브랜치

**브랜치는 작업 공간을 복사해서 따로 노는 것**이다. 내가 뭘 망가뜨려도 `master` 는 멀쩡하다.

```
master        ●───●───●───────────────●      ← 안전한 본체
                       \             /
내 브랜치                ●───●───●────┘        ← 여기서 실험
                                    (PR 로 합침)
```

```powershell
git branch                              # 지금 있는 브랜치 목록
git checkout -b feat/<아이디>/<주제>      # 새로 만들고 그리로 이동
git checkout master                     # 기존 브랜치로 이동
```

`-b` 가 "새로 만들기" 다. 이미 있는 브랜치로 갈 때는 `-b` 없이 쓴다.

> 브랜치를 옮기면 **폴더 안의 파일이 실제로 바뀐다.** 다른 브랜치에서 만든 파일이 안 보인다고 사라진 게 아니다. 그 브랜치로 돌아가면 다시 있다.

---

## 실수했을 때

가장 많이 필요한 부분이다. **거의 모든 실수는 되돌릴 수 있다.**

### 파일을 고쳤는데 그냥 되돌리고 싶다

```powershell
git checkout -- <파일이름>        # 파일 하나
git checkout -- third_party/     # 폴더 통째로
```

마지막 커밋 상태로 돌아간다. **고친 내용은 사라지니 주의.**

### `git add` 를 했는데 취소하고 싶다

```powershell
git reset
```

준비 구역에서만 빼낸다. 파일 내용은 그대로다.

### 방금 한 커밋의 메시지를 고치고 싶다

```powershell
git commit --amend -m "제대로 된 메시지"
```

**아직 push 안 했을 때만** 쓴다. 이미 올렸으면 그냥 두는 게 낫다.

### 커밋했는데 되돌리고 싶다

```powershell
git reset --soft HEAD~1
```

마지막 커밋을 취소하되 **파일 내용은 그대로 둔다.** 다시 커밋하면 된다.

### 브랜치를 잘못 만들었다

```powershell
git checkout master              # 일단 나오고
git branch -D <잘못된-브랜치>      # 삭제
```

### 뭐가 뭔지 모르겠다

일단 현재 상태를 본다.

```powershell
git status                       # 지금 상태
git log --oneline | head -10     # 최근 기록 10개
git branch                       # 어느 브랜치에 있나
```

그래도 모르겠으면 **아무것도 하지 말고 메인테이너에게 물어본다.**
`git status` 결과를 그대로 복사해서 보내면 된다. 섣불리 이것저것 치는 것보다 낫다.

---

## 충돌 (conflict)

나와 다른 사람이 **같은 파일의 같은 줄**을 고쳤을 때 생긴다. git 이 어느 쪽이 맞는지 모르니 사람에게 묻는 것이다.

```
<<<<<<< HEAD
내가 쓴 내용
=======
다른 사람이 쓴 내용
>>>>>>> master
```

이 표시가 파일에 그대로 들어간다. 해결 방법은:

1. 파일을 열어서 **`<<<<<<<`, `=======`, `>>>>>>>` 줄을 지우고** 남길 내용만 남긴다
2. `git add <파일>`
3. `git commit`

VS Code 로 열면 "Accept Current / Accept Incoming / Accept Both" 버튼이 뜬다. 그걸 누르는 게 편하다.

**자주 `git pull` 하면 충돌이 작다.** 몰아서 하면 커진다.

---

## 이 프로젝트에서 절대 하지 말 것

| 하지 말 것 | 왜 |
|---|---|
| `master` 에서 바로 작업 | 브랜치를 만들어서 한다 |
| `git push --force` | 다른 사람 작업이 사라질 수 있다 |
| `git reset --hard` (내용 확인 없이) | 고친 내용이 복구 불가능하게 사라진다 |
| 학습 결과나 영상 커밋 | 용량이 크다. `.gitignore` 가 막아 주지만 확인할 것 |

`--force` 와 `--hard` 는 **되돌릴 수 없는 명령**이다. 쓰기 전에 물어볼 것.

---

## 클릭으로 하고 싶다면

명령어가 부담스러우면 GUI 도구를 써도 된다. 하는 일은 똑같다.

| 도구 | 특징 |
|---|---|
| **VS Code** 의 Source Control 탭 (`Ctrl` + `Shift` + `G`) | 변경 내용을 보면서 커밋할 수 있다 |
| **GitHub Desktop** | 따로 설치. 더 단순하다 |

다만 **`git status` 와 `git log` 정도는 명령어로 볼 줄 아는 게 좋다.** 문제가 생겼을 때 물어보기 쉽다.

---

## 다음

- [../CONTRIBUTING.md](../CONTRIBUTING.md) — 이 프로젝트의 브랜치 규칙과 PR 3단계
- [1_setup.md](1_setup.md) — 설치
