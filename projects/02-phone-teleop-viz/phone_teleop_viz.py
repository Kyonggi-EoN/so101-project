"""
실행 (리포 루트에서):
    # 핸드폰으로 조종, 로그는 터미널
    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone_teleop_viz.py

    # 키보드로 테스트 (핸드폰 불필요), 로그는 rerun 웹 뷰어
    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone_teleop_viz.py --source keyboard --log rerun

    # 키보드 명령: on / off / x0.1 / y0.1 / z0.05
"""
import argparse
import atexit
import time

# phone library imports
from lerobot.teleoperators.phone import Phone, PhoneConfig
from lerobot.teleoperators.phone.config_phone import PhoneOS

from lerobot.teleoperators.phone.phone_processor import MapPhoneActionToRobotAction
from lerobot.utils.robot_utils import precise_sleep
from lerobot.utils.rotation import Rotation
import pinocchio as pin
import numpy as np
import placo_utils.visualization
import placo


FPS = 30.0
MAX_EE_STEP = 0.05  # end-effector 한 스텝당 최대 이동량 (m)
MAX_JOINT_VELOCITY = 2.0  # 관절 최대 속도 (rad/s, 약 170°/s). 1.0 은 조작감이 너무 느림, URDF 기본 10 은 너무 빠름
EE_BOUNDS = {"min": [0.0, -1.0, 0.05], "max": [1.0, 1.0, 1.0]}  # 작업 공간 (m). 바닥 z ≥ 5cm(책상 여유), 뒤 x ≥ 0 만 막고 나머지는 팔 도달 구가 정함
# 팔이 닿는 거리 제한 (구): 어깨 회전 중심에서 REACH_RADIUS 보다 먼 목표는 당겨온다
# ponytail: 어깨 관절이 pan 에 따라 3.5cm 원을 그리며 움직이는데 중심 하나로 근사. 여유 10% 로 덮음
SHOULDER_CENTER = np.array([0.039, 0.0, 0.117])  # pan 축 위, shoulder_lift 높이 (URDF 에서 측정)
REACH_RADIUS = 0.37  # 최대 도달 거리 0.41m (무작위 관절값 2만 개로 측정) 의 90%
REGULARIZATION_WEIGHT = 0.000001  # task 정규화 가중치
URDF_PATH = "projects/02-phone-teleop-viz/so101-description/so101_new_calib.urdf"
EE_FRAME = "gripper_frame_link"

def format_pose(T: np.ndarray | None) -> str:
    """4x4 자세를 'pos [x y z]  rot [wx wy wz]' 한 줄로. 위치는 m, 회전은 회전 벡터(rad)."""
    if T is None:
        return "-"
    pos = T[:3, 3]
    rotvec = Rotation.from_matrix(T[:3, :3]).as_rotvec()
    pos_str = " ".join(f"{v:+.3f}" for v in pos)
    rot_str = " ".join(f"{v:+.3f}" for v in rotvec)
    return f"pos [{pos_str}]  rot [{rot_str}]"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["phone", "keyboard"], default="phone",
                        help="입력 소스. keyboard 는 핸드폰 없이 테스트할 때")
    parser.add_argument("--log", choices=["terminal", "rerun"], default="terminal",
                        help="로그 출력 위치. keyboard 는 rerun 권장 (터미널 출력이 키보드 입력과 충돌)")
    return parser.parse_args()

def print_log(logger, args, action, phone_delta, current_robot_pose, new_robot_pose, actual_pose):
    if args.log == "rerun":
        logger.log(action, phone_delta, current_robot_pose, new_robot_pose, actual_pose)
    else:
        lines = [
            f"enabled            : {action['enabled']}",
            f"gripper_vel        : {action['gripper_vel']:+.1f}",
            f"phone delta        : {format_pose(phone_delta)}",
            f"current robot pose : {format_pose(current_robot_pose)}",
            f"new robot pose     : {format_pose(new_robot_pose)}",
            f"actual robot pose  : {format_pose(actual_pose)}",
        ]
        # 제자리 갱신: 커서 위치 저장(\0337) → 2줄로 이동 → 줄마다 끝까지 지우며(\033[K) 출력 → 커서 복귀(\0338)
        # 9줄 아래 키보드 입력 줄은 안 건드린다. 한 번에 출력해야 입력 스레드 출력이 중간에 안 끼어든다
        print("\0337\033[2;1H" + "\033[K\n".join(lines) + "\033[K\0338", end="", flush=True)

def limit_step(last_pos: np.ndarray, new_pos: np.ndarray, max_ee_step: float=MAX_EE_STEP) -> np.ndarray:
    """위치(3개)를 받아서, 직전 위치에서 max_ee_step 보다 멀면 방향은 그대로 두고 길이만 줄인다."""
    dpos = last_pos - new_pos
    n = float(np.linalg.norm(dpos))
    if n > max_ee_step:
        dpos = dpos / n * max_ee_step
        return last_pos - dpos
    else:
        return new_pos

def show(viz, robot):
    viz.display(robot.state.q)
    placo_utils.visualization.robot_frame_viz(robot, EE_FRAME)

class OrientationClutch:
    """방향 클러치: 누르는 순간 핸드폰 방향을 새 기준(앞 = 그 순간 핸드폰이 향한 쪽, 회전 = 0)으로 잡는다.
    lerobot Phone 은 누를 때 위치 원점만 다시 잡고, 방향은 처음 캘리브레이션 그대로 쓴다 (teleop_phone.py 355·358·359줄).
    마우스 비유: 마우스를 들었다 놓은 방향이 새 "위쪽" 이 된다."""
    def __init__(self):
        self.was_enabled = False
        self.press_rot_inv = None  # 누른 순간 핸드폰 방향의 역회전 (R_press⁻¹)

    def apply(self, phone_action: dict) -> dict:
        if phone_action["phone.enabled"] and not self.was_enabled:
            self.press_rot_inv = phone_action["phone.rot"].inv()  # 누르는 순간 방향 저장
        self.was_enabled = phone_action["phone.enabled"]

        if self.press_rot_inv is not None:
            # 위치: 캘리브레이션 축 → 누른 순간 핸드폰 축
            phone_action["phone.pos"] = self.press_rot_inv.apply(phone_action["phone.pos"])
            # 회전: 캘리브레이션부터의 회전 → 누른 순간부터의 회전 (누른 순간 = 0)
            phone_action["phone.rot"] = self.press_rot_inv * phone_action["phone.rot"]
        return phone_action

def phone_to_robot_action(phone_to_robot: MapPhoneActionToRobotAction, phone_action: dict) -> dict:
    """핸드폰 축 → 로봇 축. 들고 있는 자세: 평평하게(화면 위), 핸드폰 위쪽 끝 = 앞.
    핸드폰으로 확인 (2026-11-10): 핸드폰 축이 이미 로봇 축과 같다 → 변환 없이 그대로
    (teleop 패키지가 핸드폰 값을 FLU = 앞(x)·왼쪽(y)·위(z) 로 바꿔서 줌. 로봇 축도 x 앞, y 왼쪽, z 위)
    lerobot 매핑(x = -y, y = x)은 이 자세에서 앞뒤가 좌우로 가서 위치·회전만 덮어쓴다. enabled, gripper_vel 은 lerobot 그대로"""
    pos, rotvec = phone_action["phone.pos"], phone_action["phone.rot"].as_rotvec()  # lerobot 이 phone.* 를 pop 하므로 먼저 꺼냄
    action = phone_to_robot.action(phone_action)
    if action["enabled"]:  # 손 떼면 lerobot 이 0 으로 둔 값 그대로
        action.update(target_x=pos[0], target_y=pos[1], target_z=pos[2],
                      target_wx=rotvec[0], target_wy=rotvec[1], target_wz=rotvec[2])
    return action

def make_action_source(source: str):
    # 둘 다 같은 모양의 action dict (enabled, target_x..wz, gripper_vel) 를 돌려준다
        if source == "phone":
            #phone teleop config
            teleop_config = PhoneConfig(phone_os = PhoneOS.ANDROID)
            teleop_device = Phone(teleop_config)
    
            # phone -> robot action mapping changer
            phone_to_robot = MapPhoneActionToRobotAction(platform=teleop_config.phone_os)
    
            # Connecting the phone (캘리브레이션 터치까지 여기서 기다린다)
            teleop_device.connect()
    
            orientation_clutch = OrientationClutch()

            def read_action():
                return phone_to_robot_action(phone_to_robot, orientation_clutch.apply(teleop_device.get_action()))
            return read_action
        
        else:
            from test_src.keyboard_ik_viz import KeyboardSource
            keyboard = KeyboardSource()
            return keyboard.get_action

class IKSolver:
    def __init__(self, robot: placo.RobotWrapper):
        self.robot = robot
        self.solver = placo.KinematicsSolver(robot)
        self.solver.mask_fbase(True)
        self.solver.add_regularization_task(REGULARIZATION_WEIGHT) # task 정규화
        self.robot.set_velocity_limits(MAX_JOINT_VELOCITY)  # 모든 관절에 같은 값
        self.solver.enable_velocity_limits(True)
        self.solver.dt = 1 / FPS

        self.ee_task = self.solver.add_frame_task(EE_FRAME, np.eye(4))
        self.ee_task.configure(EE_FRAME, "soft", 0.5, 0.01)

    def solve(self, target_pose: np.ndarray):
        self.ee_task.T_world_frame = target_pose
        self.solver.solve(True)
        self.robot.update_kinematics()

class PhoneToTargetPose:
    def __init__(self, robot: placo.RobotWrapper):
        self.isEnabled = False
        self.current_robot_pose = robot.get_T_world_frame(EE_FRAME)
        self.new_robot_pose = robot.get_T_world_frame(EE_FRAME)
        self.phone_delta = np.eye(4)

    def update(self, robot: placo.RobotWrapper, action: dict):
        t = pin.exp6(np.array([action["target_x"], action["target_y"], action["target_z"], 0.0, 0.0, 0.0]))
        r = pin.exp6(np.array([0.0, 0.0, 0.0, action["target_wx"], action["target_wy"], action["target_wz"]]))
        self.phone_delta = np.array(t*r)

        if action["enabled"]:
            if not self.isEnabled:
                # Store the current pose when enabled is first pressed
                self.current_robot_pose = robot.get_T_world_frame(EE_FRAME)  # Get the current pose of the robot's end-effector
        
            self.new_robot_pose = self.current_robot_pose @ np.array(r)
            self.new_robot_pose[:3, 3] = self.new_robot_pose[:3, 3] + np.array(t)[:3, 3] 

        self.isEnabled = action["enabled"]
        return self.new_robot_pose

class SafetyFilter:
    def __init__(self, start_pose: np.ndarray):
        self.last_robot_pose = start_pose.copy()  # 첫 프레임도 최대 이동량 비교 (시작 자세가 범위 밖이어도 5cm 씩)

    def apply(self, new_robot_pose: np.ndarray) -> np.ndarray:
        # Clip the end-effector position to the defined bounds
        new_robot_pose[:3, 3] = np.clip(new_robot_pose[:3, 3], EE_BOUNDS["min"], EE_BOUNDS["max"])

        # 팔이 닿는 거리 안으로: 어깨 중심에서 너무 멀면 같은 방향으로 REACH_RADIUS 까지만
        d = new_robot_pose[:3, 3] - SHOULDER_CENTER # 어깨 중심에서 EE가 떨어진 길이 배열
        n = np.linalg.norm(d) # EE와 어깨 중심 사이의 거리 √(x² + y² + z²)
        if n > REACH_RADIUS:
            new_robot_pose[:3, 3] = SHOULDER_CENTER + d / n * REACH_RADIUS # 어깨 중심 위치 + 단위 백터 * 최대 반지름 = 최대 도달 위치

        # Limit the step size based on the last robot pose
        new_robot_pose[:3, 3] = limit_step(self.last_robot_pose[:3, 3], new_robot_pose[:3, 3])
        
        # Update the last robot pose for the next iteration
        self.last_robot_pose = new_robot_pose.copy()
        
        return new_robot_pose

def main():
    args = parse_args()

    # loading the robot
    robot = placo.RobotWrapper(URDF_PATH, placo.Flags.ignore_collisions)
    iksolver = IKSolver(robot)

    # ── 시각화 · 로그 설정 ──────────────────────────────────
    # 시각화는 입력 소스보다 먼저 (핸드폰 connect() 가 캘리브레이션 터치까지 멈추므로 브라우저를 먼저 열어 둔다)
    viz = placo_utils.visualization.robot_viz(robot)
    placo_utils.visualization.frame_viz("world", np.eye(4))

    logger = None
    if args.log == "rerun":
        from test_src.debug_log import DebugLogger
        logger = DebugLogger(web_port=9091)

    # ── ①② 입력 소스 설정 ─────────────────────────────────────
    read_action = make_action_source(args.source)

    # ── ④ 클러치 상태 ─────────────────────────────────────────
    phone_to_target = PhoneToTargetPose(robot)
    

    # ── 안전 장치 상태 ─────────────────────────────────────────
    safety_filter = SafetyFilter(phone_to_target.current_robot_pose)

    # ── Main loop ────────────────────────────────────────────
    if args.log == "terminal":
        # 화면 지우기 → 9줄부터 아래만 스크롤 영역 (키보드 입력·경고용) → 커서를 9줄로
        print("\033[2J\033[9r\033[9;1H", end="")
        atexit.register(print, "\033[r")  # 끝날 때 스크롤 영역 원래대로
    while True:
        t0 = time.perf_counter()

        # ── ①② 입력 ──
        action = read_action()

        # ── ③ 변화량 ──
        new_robot_pose = phone_to_target.update(robot,action)

        # ── 안전 장치: 공간 제한 → 최대 이동량 ──
        new_robot_pose = safety_filter.apply(new_robot_pose)

        # ── IK ──
        iksolver.solve(new_robot_pose)

        actual_pose = robot.get_T_world_frame(EE_FRAME)

        # ── 로그 · 시각화 ──
        print_log(logger, args, action, phone_to_target.phone_delta ,phone_to_target.current_robot_pose, new_robot_pose, actual_pose)
        show(viz, robot)

        precise_sleep(max (1.0 / FPS - (time.perf_counter() - t0), 0.0))

if __name__ == "__main__":
    main()
