# SO-101 프로젝트 사이트 (gh-pages)

이 브랜치는 GitHub Pages로 배포되는 **사이트 전용 브랜치**입니다. `master`와 이력을 공유하지 않는 별도 브랜치(orphan)라서
코드·문서는 하나도 없고, 웹 페이지 파일만 들어 있습니다. **`master`로 머지하지 않습니다.**

- 배포 주소: https://kyonggi-eon.github.io/so101-project/
- 코드와 문서(설치, 작업 규칙, 각 프로젝트의 실행 방법)는 `master` 브랜치에 있고, 이 사이트는 그쪽으로 링크만 겁니다.
- 디자인: EoN 홈페이지([kyonggi-eon.github.io](https://kyonggi-eon.github.io), 리포 `Kyonggi-EoN/kyonggi-eon.github.io`)의
  '프로젝트' 아래 페이지처럼 보이게 만듭니다. 주소도 같은 `kyonggi-eon.github.io` 아래(`/so101-project/`)입니다.

## 구조

Jekyll 사이트입니다. 홈페이지와 같은 원칙으로 **콘텐츠와 레이아웃을 섞지 않습니다.**

| 바꾸고 싶은 것 | 고칠 곳 | HTML/CSS 지식 |
|---|---|---|
| 프로젝트 페이지 추가 | `_templates/project.md`를 `_projects/<폴더 이름>.md`로 복사해 채움, 사진은 `assets/images/projects/` | 필요 없음 |
| 첫 화면 소개 문구 · 버튼 · '시작하기' 글 · 섹션 순서 | `index.md` (머리말과 본문) | 필요 없음 |
| 첫 화면 '영상' (유튜브) | `_data/videos.yml` — 영상 ID·날짜·길이·제목·설명 | 필요 없음 |
| 첫 화면 '진행 경과' | `_data/timeline.yml` | 필요 없음 |
| 첫 화면 '문서' 목록 | `_data/docs.yml` | 필요 없음 |
| 홈페이지 메뉴 · 푸터 연락처 | `_data/navigation.yml`, `_data/social.yml` (홈페이지와 같게 유지) | 필요 없음 |
| 이 사이트에만 있는 모양 (문서 목록 등) | `assets/css/site.css` | CSS |
| 페이지 틀 · 섹션 | `_layouts/`, `_includes/`, `_includes/sections/` | HTML |

```
.
├── index.md                 첫 화면: 제목 칸 → 영상 → 프로젝트 → 진행 경과 → 시작하기 → 문서
├── 404.md
├── _projects/               프로젝트 페이지   <이름>.md → /so101-project/projects/<이름>/
├── _templates/project.md    프로젝트 페이지 템플릿 (빌드에 포함되지 않음)
├── _data/                   videos(영상), timeline(진행 경과), docs(문서 목록),
│                            navigation·social(홈페이지 메뉴·연락처), labels(상태 이름)
├── _layouts/                default → page / project
├── _includes/               head, header, footer, sections/(videos, projects, timeline, docs), 작은 조각들
├── assets/css/site.css      이 사이트에만 있는 모양
├── assets/js/site.js        영상 재생 + 홈페이지의 메뉴·바람 스크립트를 불러옴
├── assets/images/projects/  프로젝트 사진
├── .github/workflows/pages.yml   빌드·배포
└── _config.yml              사이트 설정 (baseurl: /so101-project)
```

### 영상 올리기

동아리 유튜브 채널(@Kyonggi-EoN)에 올린 뒤 `_data/videos.yml` 맨 위에 한 덩어리를 추가합니다.
`id`는 주소 `https://youtu.be/<id>`의 `<id>` 부분입니다. 첫 화면에는 유튜브 미리보기 사진만 보이고, 누르면 그 자리에서 재생됩니다.
'진행 경과'에도 남길 만한 일이면 `_data/timeline.yml`에 한 줄 추가합니다.

### 프로젝트 페이지 올리기

`master`의 `projects/<번호>-<주제>/`가 머지되면, 이 브랜치에 그 프로젝트를 소개하는 페이지를 하나 만듭니다.

```bash
git fetch origin
git switch gh-pages
cp _templates/project.md _projects/01-basic-workflow.md   # 이름은 master의 프로젝트 폴더와 같게
# 머리말과 본문을 채우고, 사진은 assets/images/projects/에
git add _projects assets/images/projects
git commit -m "feat: 01-basic-workflow 프로젝트 페이지 추가"
git push origin gh-pages
```

- 실행 방법·막혔던 것은 `master`의 `projects/<폴더>/README.md`에 이미 있으니, 여기에는 무엇을 하는지와 결과(사진·영상)만 짧게 씁니다.
  머리말의 `folder:`에 폴더 경로를 적으면 '코드와 실행 방법' 버튼이 그 README를 엽니다.
- 사진이 있는 프로젝트는 첫 화면에 사진 카드로, 없는 프로젝트는 그 아래 목록 한 줄로 나옵니다. 순서는 `order:`(작은 수가 먼저).
- 화면 캡처에 개인 경로(`C:\Users\...`)·포트 번호·토큰 같은 사용자 고유값이 찍히지 않았는지 확인합니다.

## 메인 사이트와 맞춰 둔 것

- **CSS·JS·로고는 홈페이지 것을 그대로 불러 씁니다.** `_includes/head.html`이 홈페이지의 `/assets/css/main.css`를,
  `assets/js/site.js`가 홈페이지의 `assets/js/modules/`(메뉴 `nav.js`, 바람 `wind.js`·`wind-lines.js`)를 불러옵니다.
  그래서 홈페이지에서 색·글꼴·바람을 고치면 여기도 같이 바뀝니다. 반대로 홈페이지가 클래스 이름을 바꾸면 여기 모양이 깨질 수 있으니,
  홈페이지 디자인을 크게 바꿨으면 이 사이트도 한 번 열어 봅니다.
- 이 사이트에만 있는 모양은 `assets/css/site.css`에 두고, 색·간격은 홈페이지 토큰(`var(--…)`)만 씁니다.
  홈페이지 디자인 규칙과 좋은 예·피할 예는 그 리포의 `_refs/`에 있으니 모양을 바꾸기 전에 먼저 봅니다.
- 머리줄·푸터·제목 칸·프로젝트 카드·목록 줄: 홈페이지의 `_includes/header.html`, `footer.html`, `_layouts/page.html`,
  `_layouts/project.html`, `_includes/sections/projects.html`과 같은 마크업입니다. 로고와 메뉴는 홈페이지로 가고 '프로젝트'가 빨갛게 표시됩니다.
  홈페이지의 `content/_data/navigation.yml`이나 `social.yml`이 바뀌면 여기 `_data/navigation.yml`, `social.yml`도 손으로 같이 고칩니다.
- Jekyll 버전·`.ruby-version`·배포 방식(GitHub Actions)도 홈페이지와 같습니다. `Gemfile`은 홈페이지 것에서 RSS 플러그인(`jekyll-feed`)만 뺐습니다.

## 로컬에서 미리 보기

CSS·JS를 홈페이지에서 불러오므로 인터넷이 연결되어 있어야 제대로 보입니다.

**Ruby가 있으면** (Ruby 3.3 권장)

```bash
bundle install
bundle exec jekyll serve --livereload
# → http://localhost:4000/so101-project/
```

**Docker만 있으면**

```bash
docker run --rm -it -p 4000:4000 -v "$PWD":/srv -w /srv ruby:3.3 \
  bash -c "bundle install && bundle exec jekyll serve --host 0.0.0.0 --livereload"
```

주소 끝의 `/so101-project/`를 빼먹으면 404가 납니다. `_config.yml`을 고쳤을 때는 서버를 다시 켜야 반영됩니다.

## 배포

- `gh-pages`에 push → `.github/workflows/pages.yml`이 빌드 후 배포 (1~2분)
- `gh-pages`로 들어오는 Pull Request → 빌드만 검사하고 배포하지 않음
- 이 워크플로 파일은 이 브랜치에만 있어서 `master` 쪽 PR·push에는 돌지 않습니다.

### 처음 한 번만: 저장소 설정 (관리자)

1. **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 바꿉니다.
2. **Settings → Environments → github-pages → Deployment branches and tags**에 `gh-pages`를 추가합니다.
   이 환경은 보통 기본 브랜치(`master`)만 배포를 허용하도록 만들어집니다. 목록에 `gh-pages`가 없으면 배포 단계가
   `Branch "gh-pages" is not allowed to deploy to github-pages due to environment protection rules.`로 실패합니다.
3. Actions 탭에서 `Pages` 워크플로를 다시 실행(Re-run)하거나 `gh-pages`에 아무 커밋이나 push합니다.

홈페이지의 SO-101 카드(`content/_projects/so101-project.md`)에 `site: https://kyonggi-eon.github.io/so101-project/`를 적으면
카드와 상세 페이지에 '프로젝트 사이트' 버튼이 생기고, 다른 프로젝트 사이트의 EoN 상단 바 목록에도 나타납니다.
