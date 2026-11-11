"""방향 클러치(OrientationClutch) 확인. 핸드폰 없이 가짜 핸드폰 값으로 돌린다.

    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/test_src/test_orientation_clutch.py

실제 경로(OrientationClutch → phone_to_robot_action)를 통과시켜서 로봇 축 target_* 로 확인한다.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from phone_teleop_viz import PHONE_POSITION_SCALE as S, PHONE_ROTATION_SCALE as SR, OrientationClutch, phone_to_robot_action  # noqa: E402
from lerobot.teleoperators.phone.config_phone import PhoneOS  # noqa: E402
from lerobot.teleoperators.phone.phone_processor import MapPhoneActionToRobotAction  # noqa: E402
from lerobot.utils.rotation import Rotation  # noqa: E402

BUTTONS = {"move": True, "scale": 1.0, "reservedButtonA": False, "reservedButtonB": False}


def phone(enabled, pos, rot):
    return {"phone.enabled": enabled, "phone.pos": np.array(pos, float), "phone.rot": rot,
            "phone.raw_inputs": dict(BUTTONS)}


MAPPER = MapPhoneActionToRobotAction(platform=PhoneOS.ANDROID)


def run(clutch, action):
    return phone_to_robot_action(MAPPER, clutch.apply(action))


yaw90 = Rotation.from_rotvec([0, 0, np.pi / 2])      # 핸드폰을 왼쪽으로 90° 돌려 듦
tilt30 = Rotation.from_rotvec([np.deg2rad(30), 0, 0])  # 핸드폰을 30° 기울여 듦

# 1. 90° 돌려 들고 누른 뒤 "핸드폰 기준 앞" 으로 10cm → 로봇은 앞(+x) 으로
#    핸드폰 앞(위쪽 끝) = 캘리브레이션 축의 +x (FLU, 핸드폰으로 확인)
forward = yaw90.apply(np.array([0.1, 0, 0]))
c = OrientationClutch()
run(c, phone(True, [0, 0, 0], yaw90))                 # 누르는 순간
a = run(c, phone(True, forward, yaw90))               # 앞으로 밂
assert np.allclose([a["target_x"], a["target_y"], a["target_z"]], [0.1 * S, 0, 0], atol=1e-9), a
# 비교: 클러치 없으면 왼쪽(+y) 으로 감
b = phone_to_robot_action(MAPPER, phone(True, forward, yaw90))
assert np.allclose([b["target_x"], b["target_y"]], [0, 0.1 * S], atol=1e-9), b

# 2. 30° 기울여 들고 누르기만 함 → 회전 목표 0 (그리퍼 안 튐)
c = OrientationClutch()
a = run(c, phone(True, [0, 0, 0], tilt30))
assert np.allclose([a["target_wx"], a["target_wy"], a["target_wz"]], 0, atol=1e-9), a
# 거기서 10° 더 기울이면 회전 목표는 10° 만 (× 회전 배율)
a = run(c, phone(True, [0, 0, 0], Rotation.from_rotvec([np.deg2rad(40), 0, 0])))
assert np.isclose(np.linalg.norm([a["target_wx"], a["target_wy"], a["target_wz"]]), np.deg2rad(10) * SR), a

# 3. 손 뗐다가 다른 방향으로 다시 누르면 기준이 새로 잡힘
run(c, phone(False, [0, 0, 0], tilt30))
a = run(c, phone(True, [0, 0, 0], yaw90))
assert np.allclose([a["target_wx"], a["target_wy"], a["target_wz"]], 0, atol=1e-9), a

# 4. 축 매핑 (클러치 기준 0°): 핸드폰 위쪽 끝(+x) → 로봇 앞, 핸드폰 왼쪽(+y) → 로봇 왼쪽, 위 → 위
c = OrientationClutch()
run(c, phone(True, [0, 0, 0], Rotation.from_rotvec([0, 0, 0])))
for phone_pos, robot_xyz in [([0.1, 0, 0], [0.1, 0, 0]), ([0, 0.1, 0], [0, 0.1, 0]), ([0, 0, 0.1], [0, 0, 0.1])]:
    a = run(c, phone(True, phone_pos, Rotation.from_rotvec([0, 0, 0])))
    assert np.allclose([a["target_x"], a["target_y"], a["target_z"]], np.array(robot_xyz) * S, atol=1e-9), (phone_pos, a)
# 손 떼면 0
a = run(c, phone(False, [0.1, 0, 0], Rotation.from_rotvec([0, 0, 0.3])))
assert a["target_x"] == 0 and a["target_wz"] == 0, a

# 5. 60° 숙인 채(+ 왼쪽 90° 돌려) 누르고 손을 앞으로 → 로봇도 앞으로만 (위로 새면 안 됨)
pitched = yaw90 * Rotation.from_rotvec([0, np.deg2rad(60), 0])
c = OrientationClutch()
run(c, phone(True, [0, 0, 0], pitched))
a = run(c, phone(True, yaw90.apply([0.1, 0, 0]), pitched))   # 손은 수평으로 "핸드폰이 향한 쪽" 10cm
assert np.allclose([a["target_x"], a["target_y"], a["target_z"]], [0.1 * S, 0, 0], atol=1e-9), a
# 거기서 10° 더 숙이면 회전은 숙임 10° 만
a = run(c, phone(True, [0, 0, 0], yaw90 * Rotation.from_rotvec([0, np.deg2rad(70), 0])))
assert np.allclose([a["target_wx"], a["target_wy"], a["target_wz"]], [0, np.deg2rad(10) * SR, 0], atol=1e-9), a

print("OK: 방향 클러치 + 축 매핑 5개 확인 통과")
