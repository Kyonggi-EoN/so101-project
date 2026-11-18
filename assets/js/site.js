// 사이트 공통 스크립트. EoN 홈페이지의 기능 파일(assets/js/modules/)을 그대로 불러 씁니다.
// 그래서 홈페이지에서 메뉴·바람을 고치면 여기도 같이 바뀝니다.
// - 실제 사이트에서는 같은 주소(kyonggi-eon.github.io)라 바로 불러오고, 로컬 미리보기에서도
//   GitHub Pages가 다른 주소의 요청을 허용해 줘서 불러올 수 있습니다.
// - 파일마다 따로 불러와서, 하나가 받아지지 않아도 나머지는 그대로 움직입니다(못 불러오면 그 기능만 빠짐).
const MAIN = "https://kyonggi-eon.github.io/assets/js/modules/";

const FEATURES = [
  ["nav.js", "initNav"], // 좁은 화면 메뉴 열고 닫기
  ["wind.js", "initWind"], // 제목 칸 오른쪽 바람 줄기 떼: canvas[data-wind]
  ["wind-lines.js", "initWindLines"], // 섹션 제목줄 아래·푸터 위 선의 줄기: <body data-wind-lines>
];

for (const [file, init] of FEATURES) {
  import(MAIN + file)
    .then((m) => m[init]())
    .catch((err) => console.error(`${file}:`, err));
}
