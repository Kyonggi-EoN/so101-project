# third_party/lerobot

이 폴더의 `lerobot/` 는 업스트림 LeRobot의 파이썬 패키지(`src/lerobot`)를 **그대로 복사한 것**이다.

<!-- BEGIN:AUTO -->
| | |
|---|---|
| 원본 | https://github.com/huggingface/lerobot |
| 커밋 | `5aa74557f84c54d4b458f8b9643c5aa2982acfed` |
| 커밋 날짜 | 2026-09-17 |
| 가져온 날짜 | 2026-09-19 |
| 파일 수 | .py 537개 |
| 라이선스 | Apache-2.0 - `third_party/LICENSE` |
<!-- END:AUTO -->

> 위 표는 `tools/update_lerobot.ps1` 이 자동으로 갱신한다. 손으로 고치지 말 것.

## 왜 복사해서 들고 있나

동아리원 전원이 코드를 읽으면서 개발하기 위해서다. 의존성으로 받으면 코드가
각자 `.venv/` 안에 들어가서 GitHub에서 링크를 걸 수 없다.

## 건드리지 말 것

여기는 **읽기 전용**이다. `CODEOWNERS` 로 보호돼 있고, 수정은 메인테이너만 한다.
`print` 를 찍어보는 건 자유다 — editable 설치라 바로 반영된다. 다만 커밋하지 말 것.

작업은 `projects/` 안에서 한다.

## 버전 올리기

```powershell
.\tools\update_lerobot.ps1 -Rev <새 커밋 해시>
uv lock
# 로봇 붙여서 텔레오퍼레이션 -> 짧은 녹화 -> rollout 한 바퀴 검증한 뒤 커밋
```

스크립트가 업스트림 `pyproject.toml` 의존성 diff를 출력한다. 거기 변화가 있으면
우리 `pyproject.toml` 에 반영할지 판단해야 한다. 우리가 바꾼 4곳은
`pyproject.toml` 헤더에 적혀 있다.

## 포함되지 않은 것

업스트림 리포 루트의 파일들(`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
`docs/`, `examples/`, `media/`, `tests/`)은 `src/lerobot` 바깥이라 복사 대상이 아니다.
동아리 문서는 리포 루트에 따로 쓴다.
