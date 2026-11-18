---
# ─────────────────────────────────────────────────────────────
# 프로젝트 페이지 템플릿
# 1) 이 파일을 _projects/<폴더 이름>.md 로 복사합니다.
#    폴더 이름은 master 브랜치의 projects/<번호>-<주제> 와 같게 합니다. 예: _projects/01-basic-workflow.md
#    파일 이름이 주소가 됩니다 → https://kyonggi-eon.github.io/so101-project/projects/01-basic-workflow/
# 2) 아래 값을 채우고, 쓰지 않는 줄은 지웁니다. # 뒤는 설명이라 지워도 됩니다.
# 3) 본문에는 무엇을 하는지·결과(사진·영상)만 짧게 씁니다.
#    실행 방법과 막혔던 것은 master의 projects/<폴더>/README.md 에 있으니 그쪽 링크로 충분합니다.
# ─────────────────────────────────────────────────────────────
title: 프로젝트 제목
summary: 한두 문장 요약. 첫 화면 카드와 이 페이지 제목 아래에 나옵니다.
folder: projects/01-basic-workflow     # master 브랜치의 프로젝트 폴더. '코드와 실행 방법' 버튼이 이 폴더를 엽니다
members: [깃허브아이디]                  # GitHub 아이디. 여러 명이면 [id1, id2]
status: active                         # active(진행 중) · done(완료) · archived(보관)
year: 2026
tags: [Robotics]
image: /assets/images/projects/01-basic-workflow.jpg   # 없으면 이 줄을 지웁니다. 사진이 없으면 첫 화면에 목록 한 줄로 나옵니다
image_alt: 사진 설명 (화면 낭독기가 읽습니다)
video: https://www.youtube.com/watch?v=...             # 없으면 지웁니다
order: 1                               # 첫 화면에 보일 순서 (작은 수가 먼저)
---

무엇을 하는 프로젝트인지 두세 문장으로 씁니다.

![사진 설명]({{ '/assets/images/projects/01-basic-workflow.jpg' | relative_url }})

## 결과

어떻게 동작하는지, 무엇을 확인했는지 씁니다.
