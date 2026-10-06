"""
리팩토링 검증용: 키보드 입력을 '프레임 번호' 로 고정해서 실행하고, 매 프레임 목표 자세를 비교한다.
실시간 입력은 시작 속도에 따라 결과가 흔들리지만, 이건 몇 번을 돌려도 같은 결과가 나온다.

사용법 1 — 그냥 실행 (VS Code 실행 버튼도 됨):
    python projects/02-phone-teleop-viz/test_src/frame_replay.py
    → 마지막 커밋(HEAD)의 phone_teleop_viz.py 와 지금 파일을 비교해서 IDENTICAL / DIFFERENT 출력

사용법 2 — 파일 하나만 돌려서 결과 저장:
    python projects/02-phone-teleop-viz/test_src/frame_replay.py <대상 스크립트> <결과 파일>

전제: 대상 스크립트가 --source keyboard 에서 test_src.keyboard_ik_viz.KeyboardSource 를 쓰고,
터미널 로그에 "new robot pose" 줄을 출력한다. (로그 형식을 바꾸면 아래 fake_print 도 맞춰야 한다)
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent          # projects/02-phone-teleop-viz
REPO_ROOT = PROJECT_DIR.parent.parent                         # 리포 루트 (URDF 경로가 여기 기준)
MAIN_SCRIPT = PROJECT_DIR / "phone_teleop_viz.py"
EXPECTED_FRAMES = 260

# (시작 프레임, enabled, x, y, z) — 다음 줄의 시작 프레임 전까지 유지. enabled=None 이면 종료
SCRIPT = [
    (0, False, 0, 0, 0),
    (30, True, 0, 0, 0),
    (31, True, -0.2, 0, 0),     # 뒤로 20cm (최대 이동량으로 나뉘어 이동)
    (90, False, 0, 0, 0),
    (100, True, 0, 0, 0),
    (101, True, 0, 0, -0.3),    # 아래로 30cm (z 최소에서 잘림)
    (170, False, 0, 0, 0),
    (180, True, 0, 0, 0),
    (181, True, 0, 0.4, 0),     # 왼쪽 40cm (y 최대에서 잘림)
    (EXPECTED_FRAMES, None, 0, 0, 0),
]


def run_one(target_script: str, out_path: str) -> None:
    """대상 스크립트를 대본 입력으로 실행하고, 매 프레임 'new robot pose' 를 out_path 에 쓴다."""
    import builtins
    import runpy

    sys.path.insert(0, str(PROJECT_DIR))
    os.chdir(REPO_ROOT)

    import lerobot.utils.robot_utils as robot_utils
    import placo_utils.visualization as pv
    import test_src.keyboard_ik_viz as kb

    frame = [0]
    written = [0]

    def scripted_get_action(self):
        f = frame[0]
        frame[0] += 1
        _, enabled, x, y, z = [s for s in SCRIPT if s[0] <= f][-1]
        if enabled is None:
            raise SystemExit(0)
        return {"enabled": enabled, "target_x": x, "target_y": y, "target_z": z,
                "target_wx": 0.0, "target_wy": 0.0, "target_wz": 0.0, "gripper_vel": 0.0}

    # 키보드 입력 스레드 대신 대본, 시각화·대기 끄기 (빠르고 결정적으로)
    kb.KeyboardSource.__init__ = lambda self: None
    kb.KeyboardSource.get_action = scripted_get_action
    robot_utils.precise_sleep = lambda seconds: None
    pv.robot_viz = lambda robot, name="robot": type("NoViz", (), {"display": lambda self, q: None})()
    pv.frame_viz = lambda *args, **kwargs: None
    pv.robot_frame_viz = lambda *args, **kwargs: None

    out = open(out_path, "w")
    real_print = builtins.print

    def fake_print(*args, **kwargs):
        line = " ".join(str(a) for a in args)
        if line.startswith("new robot pose"):
            out.write(line.split(": ", 1)[1] + "\n")
            written[0] += 1

    builtins.print = fake_print
    sys.argv = [target_script, "--source", "keyboard", "--log", "terminal"]
    try:
        runpy.run_path(target_script, run_name="__main__")
    finally:
        out.close()
        builtins.print = real_print
        print(f"  frames: {written[0]} / {EXPECTED_FRAMES}", file=sys.stderr)


def run_in_subprocess(target_script: str, out_path: str) -> bool:
    """매번 새 파이썬에서 실행 (패치·전역 상태가 섞이지 않게). 성공하면 True."""
    env = dict(os.environ, GLIBC_TUNABLES="glibc.rtld.execstack=2")  # hebi import 우회 (docs.md 3번)
    result = subprocess.run([sys.executable, __file__, target_script, out_path], env=env, cwd=REPO_ROOT)
    return result.returncode == 0


def compare_head_vs_working() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="frame_replay_"))
    before_py, before_txt, after_txt = tmp / "before.py", tmp / "before.txt", tmp / "after.txt"

    rel = MAIN_SCRIPT.relative_to(REPO_ROOT).as_posix()
    head_source = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO_ROOT,
                                 capture_output=True, text=True, check=True).stdout
    before_py.write_text(head_source)

    print("[1/2] 마지막 커밋 (HEAD)")
    ok_before = run_in_subprocess(str(before_py), str(before_txt))
    print("[2/2] 지금 파일")
    ok_after = run_in_subprocess(str(MAIN_SCRIPT), str(after_txt))

    if not (ok_before and ok_after):
        print("\nERROR: 실행 중 에러 (위 메시지 참고)")
        sys.exit(1)

    before = before_txt.read_text().splitlines()
    after = after_txt.read_text().splitlines()
    if before == after:
        print(f"\nIDENTICAL ({len(after)} 프레임 모두 같음)")
        return

    print("\nDIFFERENT — 처음 달라지는 곳:")
    for i, (b, a) in enumerate(zip(before, after)):
        if b != a:
            for j in range(i, min(i + 5, len(before), len(after))):
                print(f"  frame {j:3d}  HEAD : {before[j]}")
                print(f"             지금 : {after[j]}")
            break
    else:
        print(f"  프레임 수가 다름: HEAD {len(before)} / 지금 {len(after)}")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        run_one(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 1:
        compare_head_vs_working()
    else:
        print(__doc__)
        sys.exit(2)
