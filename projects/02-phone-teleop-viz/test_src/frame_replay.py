"""
리팩토링 검증용: 키보드 입력을 '프레임 번호' 로 고정해서 실행하고, 매 프레임 목표 자세를 파일로 남긴다.
실시간 입력은 시작 속도에 따라 결과가 흔들리지만, 이건 몇 번을 돌려도 같은 결과가 나온다.

사용법 (리포 루트에서. hebi 때문에 GLIBC_TUNABLES 필요할 수 있음 — docs.md 3번):
    export GLIBC_TUNABLES=glibc.rtld.execstack=2

    # 1) 마지막 커밋 버전을 꺼내서 기준 결과 만들기
    git show HEAD:projects/02-phone-teleop-viz/phone_teleop_viz.py > /tmp/before.py
    uv run python projects/02-phone-teleop-viz/test_src/frame_replay.py /tmp/before.py /tmp/before.txt

    # 2) 고친 버전 결과
    uv run python projects/02-phone-teleop-viz/test_src/frame_replay.py projects/02-phone-teleop-viz/phone_teleop_viz.py /tmp/after.txt

    # 3) 비교 — IDENTICAL 이 나오면 동작이 같다
    cmp /tmp/before.txt /tmp/after.txt && echo IDENTICAL

끝나면 "frames: 260" 이 나와야 정상. 그보다 적으면 중간에 에러로 멈춘 것 (에러 메시지가 같이 출력됨).

전제: 대상 스크립트가 --source keyboard 에서 test_src.keyboard_ik_viz.KeyboardSource 를 쓰고,
터미널 로그에 "new robot pose" 줄을 출력한다. (로그 형식을 바꾸면 아래 fake_print 도 맞춰야 한다)
"""
import builtins
import runpy
import sys

sys.path.insert(0, "projects/02-phone-teleop-viz")

import lerobot.utils.robot_utils as robot_utils
import placo_utils.visualization as pv
import test_src.keyboard_ik_viz as kb

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
    (260, None, 0, 0, 0),
]

_frame = [0]
_written = [0]


def scripted_get_action(self):
    f = _frame[0]
    _frame[0] += 1
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

target_script, out_path = sys.argv[1], sys.argv[2]
out = open(out_path, "w")
real_print = builtins.print


def fake_print(*args, **kwargs):
    line = " ".join(str(a) for a in args)
    if line.startswith("new robot pose"):
        out.write(line.split(": ", 1)[1] + "\n")
        _written[0] += 1


builtins.print = fake_print
sys.argv = [target_script, "--source", "keyboard", "--log", "terminal"]
try:
    runpy.run_path(target_script, run_name="__main__")
finally:
    out.close()
    builtins.print = real_print
    print(f"frames: {_written[0]}  (정상: 260, 멈춘 프레임: {_frame[0] - 1})", file=sys.stderr)
