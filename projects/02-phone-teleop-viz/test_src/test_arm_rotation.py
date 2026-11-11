"""핸드폰 회전 → 로봇 회전 확인 (arm_rotation). 핸드폰 없이 실제 IK 로 돌린다.

    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/test_src/test_arm_rotation.py

옆으로 돌리기 → 팔 전체(shoulder_pan), 앞으로 숙이기 → 손목 숙임, 양옆 기울이기 → 그리퍼 비틀기(wrist_roll)
"""
import sys
from pathlib import Path

import numpy as np
import placo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import phone_teleop_viz as m  # noqa: E402

J = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]


def turn(rotvec_deg):
    """시작 자세에서 누르고, 핸드폰을 rotvec 만큼 돌린 채 2초 → (관절 변화°, 끝 위치 변화, 그리퍼 뻗은 방향)"""
    robot = placo.RobotWrapper(m.URDF_PATH, placo.Flags.ignore_collisions)
    robot.update_kinematics()
    ik, p2t = m.IKSolver(robot), m.PhoneToTargetPose(robot)
    sf = m.SafetyFilter(robot.get_T_world_frame(m.EE_FRAME))
    q0 = np.array([robot.get_joint(j) for j in J])
    p0 = robot.get_T_world_frame(m.EE_FRAME)[:3, 3].copy()
    w = np.deg2rad(rotvec_deg)
    for f in range(60):
        s = min(f / 20, 1.0)  # 0.7초 동안 천천히 돌림
        a = {"enabled": True, "target_x": 0.0, "target_y": 0.0, "target_z": 0.0,
             "target_wx": w[0] * s, "target_wy": w[1] * s, "target_wz": w[2] * s}
        ik.solve(sf.apply(p2t.update(robot, a)))
    T = robot.get_T_world_frame(m.EE_FRAME)
    dq = dict(zip(J, np.rad2deg(np.array([robot.get_joint(j) for j in J]) - q0)))
    return dq, T[:3, 3] - p0, T[:3, 2]


# 1. 옆으로 30° 돌리기 → 팔 전체가 왼쪽으로 30° (끝 위치도 원호로 왼쪽), 다른 관절은 거의 그대로
dq, dp, z = turn([0, 0, 30])
print("옆으로 30°  :", {k: round(v) for k, v in dq.items()}, "끝 이동(cm)", np.round(dp * 100, 1))
assert abs(abs(dq["shoulder_pan"]) - 30) < 3 and dp[1] > 0.1, dq
assert all(abs(dq[j]) < 3 for j in J if j != "shoulder_pan"), dq

# 2. 앞으로 20° 숙이기 → 그리퍼 끝은 제자리, 뻗은 방향이 20° 아래로
dq, dp, z = turn([0, 20, 0])
print("앞으로 20°  :", {k: round(v) for k, v in dq.items()}, "끝 이동(cm)", np.round(dp * 100, 1))
assert np.linalg.norm(dp) < 0.01, dp
assert abs(np.rad2deg(np.arcsin(-z[2])) - 20) < 3, z  # 시작 때 그리퍼는 수평으로 앞을 봄

# 3. 오른쪽으로 20° 기울이기(x 축 +) → 그리퍼만 20° 비틀림
dq, dp, z = turn([20, 0, 0])
print("기울이기 20°:", {k: round(v) for k, v in dq.items()}, "끝 이동(cm)", np.round(dp * 100, 1))
assert abs(abs(dq["wrist_roll"]) - 20) < 3 and np.linalg.norm(dp) < 0.01, dq
assert all(abs(dq[j]) < 3 for j in J if j != "wrist_roll"), dq

# 4. 쌓임 + 각도 끝: 60° 숙이기를 두 번 (누르고-숙이고-떼고) → 120° 가 아니라 90° 에서 멈춤
robot = placo.RobotWrapper(m.URDF_PATH, placo.Flags.ignore_collisions)
robot.update_kinematics()
ik, p2t = m.IKSolver(robot), m.PhoneToTargetPose(robot)
off = {"enabled": False, "target_x": 0.0, "target_y": 0.0, "target_z": 0.0, "target_wx": 0.0, "target_wy": 0.0, "target_wz": 0.0}


def tilt(pitch_deg, enabled=True):
    a = dict(off, enabled=enabled, target_wy=np.deg2rad(pitch_deg))
    for _ in range(60):
        ik.solve(p2t.update(robot, a))
    return np.rad2deg(m.gripper_angles(p2t.new_robot_pose[:3, :3])[1])


t1 = tilt(60)
tilt(0, enabled=False)                      # 떼고 핸드폰 평평하게
t2 = tilt(60)                               # 다시 누르고 60°
t3 = tilt(50)                               # 끝에서 10° 되돌림
print(f"숙임 쌓임   : 1번째 {t1:.0f}°, 2번째 {t2:.0f}° (끝 90°), 10° 되돌리면 {t3:.0f}°")
assert abs(t1 - 60) < 4 and abs(t2 - 90) < 1e-6 and abs(t3 - 80) < 1e-6, (t1, t2, t3)

# 5. 옆으로 돌리기도 각도 끝에서 멈추고 넘친 만큼 버림 (위치·숙임과 같은 규칙, 마우스처럼)
#    130° → pan 90° 에서 멈춤 (40° 버림), 10° 되돌리면 바로 80°, 120° 더 되돌리면 80 - 120 = -40°
#    되돌려도 그리퍼 끝은 처음 원호 위 (높이·pan 축까지 거리 그대로. 예전엔 벽에 잘린 양이 위치에 쌓여 11cm 어긋남)
#    200° (yaw 가 +180 → -180 으로 넘어감) 까지 돌려도 팔이 반대쪽으로 튀지 않음: -40 + 200 → 90° 에서 멈춤
robot = placo.RobotWrapper(m.URDF_PATH, placo.Flags.ignore_collisions)
robot.update_kinematics()
ik, p2t = m.IKSolver(robot), m.PhoneToTargetPose(robot)
sf = m.SafetyFilter(robot.get_T_world_frame(m.EE_FRAME))
p0 = robot.get_T_world_frame(m.EE_FRAME)[:3, 3].copy()


def yaw_to(deg_from, deg_to, frames=3):
    """누른 채 핸드폰 yaw 를 5° 씩 천천히 돌림 (rotvec z = -180~180 으로 감싼 값, 실제 핸드폰처럼)"""
    for d in np.arange(deg_from, deg_to + np.sign(deg_to - deg_from), 5 * np.sign(deg_to - deg_from)):
        wz = (np.deg2rad(d) + np.pi) % (2 * np.pi) - np.pi
        for _ in range(frames):
            ik.solve(sf.apply(p2t.update(robot, dict(off, enabled=True, target_wz=wz))))
    for _ in range(40):
        ik.solve(sf.apply(p2t.update(robot, dict(off, enabled=True, target_wz=wz))))
    return -np.rad2deg(robot.get_joint("shoulder_pan"))  # pan 축이 월드 -z (URDF) → 왼쪽 + 로


pan1 = yaw_to(0, 130)
pan2 = yaw_to(130, 120)
pan3 = yaw_to(120, 0)
p3 = robot.get_T_world_frame(m.EE_FRAME)[:3, 3]
dp = np.linalg.norm(m.PAN_AXIS + m.rot([0, 0, 1], np.deg2rad(pan3)) @ (p0 - m.PAN_AXIS) - p3)  # 원호 위 기대 위치와 차이
pan4 = yaw_to(0, 200)
print(f"옆으로 돌림 : 130° → pan {pan1:.0f}°, 120° → {pan2:.0f}°, 0° → {pan3:.0f}° (원호에서 {dp*100:.1f}cm), 200° → {pan4:.0f}°")
assert abs(pan1 - 90) < 3 and abs(pan2 - 80) < 3 and abs(pan3 + 40) < 3 and dp < 0.01, (pan1, pan2, pan3, dp)
assert abs(pan4 - 90) < 3, pan4

# gripper_angles ↔ gripper_rotation 서로 역 (범위 안 아무 값)
for h, tl, tw in [(0.3, 0.5, -1.0), (-2.0, -0.4, 1.2), (1.0, 1.4, 0.2)]:
    assert np.allclose(m.gripper_angles(m.gripper_rotation(h, tl, tw)), (h, tl, tw)), (h, tl, tw)

print("OK: 옆으로 돌리기 → 팔 전체, 숙이기 → 손목, 기울이기 → 그리퍼 비틀기, 숙임은 90° 에서 멈추고 되돌리면 바로 반응")
