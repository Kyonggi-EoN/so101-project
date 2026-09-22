# projects/

**작업 구역.** 여기는 자유롭게 만들고 고친다. 프로젝트마다 폴더를 하나씩 만든다.

이 폴더 밖(`third_party/`, `docs/`, `calibration/`, `pyproject.toml` 등)은 메인테이너가 관리한다.

---

## 새 프로젝트 시작하기

### 1. 양식 복사

`<번호>` 는 아래 목록의 다음 순번, `<주제>` 는 영어 소문자와 하이픈으로 쓴다.
**꺾쇠(`<>`)는 지우고** 자기 값을 넣는다.

```powershell
Copy-Item -Recurse projects\_TEMPLATE projects\<번호>-<주제>
```

예: `Copy-Item -Recurse projects\_TEMPLATE projects\03-hand-tracking`

`_TEMPLATE/README.md` 에 채워야 할 항목 6개가 들어 있다.

### 2. 브랜치 만들기

폴더 이름과 맞추면 알아보기 쉽다.

`<깃허브-아이디>` 는 내 GitHub 계정 이름, `<주제>` 는 위 폴더 이름과 같게 한다.

```powershell
git checkout master
git pull
git checkout -b feat/<깃허브-아이디>/<주제>
```

예: `git checkout -b feat/jsjin7371/hand-tracking`

### 3. 작업하고 PR

완성되면 `master` 로 PR 을 연다. **검토를 통과해야 머지된다.**

| | 단계 | 언제 |
|---|---|---|
| ① | 코드·문서 검토 | 항상 |
| ② | 다른 컴퓨터에서 재현 | `feat/` 만 |
| ③ | 세미나 발표 | `feat/` 만 |

새 프로젝트(`feat/`)는 3단계를 전부 거친다. 문서·버그 수정(`docs/`, `fix/`)은 ① 만 통과하면 된다.

자세한 건 [../CONTRIBUTING.md](../CONTRIBUTING.md) 참고.

---

## 폴더 이름

```
<번호>-<주제>
```

번호는 순서대로 붙인다. 주제는 영어 소문자에 하이픈을 쓴다.

```
01-basic-workflow
02-phone-teleop
03-hand-tracking
```

---

## 목록

<!-- 프로젝트가 머지되면 여기에 한 줄 추가한다 -->

| 폴더 | 내용 | 만든 사람 |
|---|---|---|
| | | |
