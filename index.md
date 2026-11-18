---
title: SO-101 로봇팔
eyebrow: ← 프로젝트
eyebrow_url: https://kyonggi-eon.github.io/projects/
description: 동아리에서 함께 쓰는 SO-101 로봇팔로 부원들이 각자 프로젝트를 만들어 올립니다. 로봇팔이 없어도 설치와 학습까지는 해 볼 수 있습니다.
permalink: /
status: active
year: 2026
tags: [Robotics, Python, LeRobot]
actions:
  - label: 시작하기
    url: "#start"
    icon: arrow
  - label: GitHub
    url: https://github.com/Kyonggi-EoN/so101-project
    icon: github
    style: ghost
sections:
  - videos
  - projects
  - timeline
  - type: content
    id: start
    title: 시작하기
  - docs
---

uv(파이썬 패키지를 관리해 주는 프로그램)가 설치되어 있다면 아래 세 줄로 준비가 끝납니다.

```powershell
git clone https://github.com/Kyonggi-EoN/so101-project.git
cd so101-project
uv sync
```

처음이거나 막히면 [설치하기 문서](https://github.com/Kyonggi-EoN/so101-project/blob/master/docs/1_setup.md)를 처음부터 따라 하세요(20분). git·uv 설치부터 그래픽카드 설정까지 들어 있습니다.

AI 코딩 도구를 쓴다면 작업을 시키기 전에 [AGENTS.md](https://github.com/Kyonggi-EoN/so101-project/blob/master/AGENTS.md)를 먼저 읽게 하세요. 건드리면 안 되는 폴더와 로봇팔을 다룰 때 지킬 것이 적혀 있습니다.
