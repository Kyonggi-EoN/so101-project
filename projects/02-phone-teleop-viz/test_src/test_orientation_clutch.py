"""방향 클러치(OrientationClutch) 확인. 핸드폰 없이 가짜 핸드폰 값으로 돌린다.

    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/test_src/test_orientation_clutch.py

lerobot 의 실제 매핑(MapPhoneActionToRobotAction)까지 통과시켜서 로봇 축 target_* 로 확인한다.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from phone_teleop_viz import OrientationClutch  # noqa: E402
from lerobot.teleoperators.phone.config_phone import PhoneOS  # noqa: E402
from lerobot.teleoperators.phone.phone_processor import MapPhoneActionToRobotAction  # noqa: E402
from lerobot.utils.rotation import Rotation  # noqa: E402

BUTTONS = {"move": True, "scale": 1.0, "reservedButtonA": False, "reservedButtonB": False}


def phone(enabled, pos, rot):
    return {"phone.enabled": enabled, "phone.pos": np.array(pos, float), "phone.rot": rot,
            "phone.raw_inputs": dict(BUTTONS)}


def run(clutch, action):
    return MapPhoneActionToRobotAction(platform=PhoneOS.ANDROID).action(clutch.apply(action))


yaw90 = Rotation.from_rotvec([0, 0, np.pi / 2])      # 핸드폰을 왼쪽으로 90° 돌려 듦
tilt30 = Rotation.from_rotvec([np.deg2rad(30), 0, 0])  # 핸드폰을 30° 기울여 듦

# 1. 90° 돌려 들고 누른 뒤 "핸드폰 기준 앞" 으로 10cm → 로봇은 앞(+x) 으로
#    핸드폰 앞 = 캘리브레이션 축의 -y. 90° 돌린 핸드폰의 앞은 캘리브레이션 축으로 +x
forward = yaw90.apply(np.array([0, -0.1, 0]))
c = OrientationClutch()
run(c, phone(True, [0, 0, 0], yaw90))                 # 누르는 순간
a = run(c, phone(True, forward, yaw90))               # 앞으로 밂
assert np.allclose([a["target_x"], a["target_y"], a["target_z"]], [0.1, 0, 0], atol=1e-9), a
# 비교: 클러치 없으면 왼쪽(+y) 으로 감
b = MapPhoneActionToRobotAction(platform=PhoneOS.ANDROID).action(phone(True, forward, yaw90))
assert np.allclose([b["target_x"], b["target_y"]], [0, 0.1], atol=1e-9), b

# 2. 30° 기울여 들고 누르기만 함 → 회전 목표 0 (그리퍼 안 튐)
c = OrientationClutch()
a = run(c, phone(True, [0, 0, 0], tilt30))
assert np.allclose([a["target_wx"], a["target_wy"], a["target_wz"]], 0, atol=1e-9), a
# 거기서 10° 더 기울이면 회전 목표는 10° 만
a = run(c, phone(True, [0, 0, 0], Rotation.from_rotvec([np.deg2rad(40), 0, 0])))
assert np.isclose(np.linalg.norm([a["target_wx"], a["target_wy"], a["target_wz"]]), np.deg2rad(10)), a

# 3. 손 뗐다가 다른 방향으로 다시 누르면 기준이 새로 잡힘
run(c, phone(False, [0, 0, 0], tilt30))
a = run(c, phone(True, [0, 0, 0], yaw90))
assert np.allclose([a["target_wx"], a["target_wy"], a["target_wz"]], 0, atol=1e-9), a

print("OK: 방향 클러치 3개 확인 통과")
