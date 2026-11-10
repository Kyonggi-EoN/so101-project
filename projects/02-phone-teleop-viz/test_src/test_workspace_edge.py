"""작업 공간 끝 확인: 벽에서 멈추고, 손을 되돌리면 로봇이 바로 따라와야 한다 (마우스가 화면 끝에서 멈추듯).

    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/test_src/test_workspace_edge.py
"""
import sys
from pathlib import Path

import numpy as np
import placo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import phone_teleop_viz as m  # noqa: E402

robot = placo.RobotWrapper(m.URDF_PATH, placo.Flags.ignore_collisions)
robot.update_kinematics()
start = robot.get_T_world_frame(m.EE_FRAME).copy()
p2t = m.PhoneToTargetPose(robot)


def hand(x):  # 키보드/핸드폰과 같은 action: 누른 순간부터 x 만큼 앞으로
    return {"enabled": True, "target_x": x, "target_y": 0.0, "target_z": 0.0,
            "target_wx": 0.0, "target_wy": 0.0, "target_wz": 0.0}


p2t.update(robot, hand(0.0))                    # 누르는 순간
edge = p2t.update(robot, hand(0.5))[0, 3]       # 손이 50cm 앞으로 (벽 밖)
assert np.isclose(np.linalg.norm(p2t.new_robot_pose[:3, 3] - m.SHOULDER_CENTER), m.REACH_RADIUS), "벽에서 멈춰야 함"
back = p2t.update(robot, hand(0.45))[0, 3]      # 5cm 되돌림
assert np.isclose(edge - back, 0.05), f"5cm 되돌리면 바로 5cm 와야 함 (edge {edge:.3f}, back {back:.3f})"

# 기준을 바꿔도 placo 내부 값은 그대로 (get_T_world_frame 이 복사본을 주는지)
assert np.allclose(robot.get_T_world_frame(m.EE_FRAME), start)

print(f"OK: 벽 x={edge:.3f} → 5cm 되돌리면 x={back:.3f}")
