"""
실행 (리포 루트에서):
    # 핸드폰으로 조종, 로그는 터미널
    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone_teleop_viz.py

    # 키보드로 테스트 (핸드폰 불필요), 로그는 rerun 웹 뷰어
    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone_teleop_viz.py --source keyboard --log rerun

    # 키보드 명령: on / off / x0.1 / y0.1 / z0.05
"""
import argparse
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
        # print log (제자리 갱신: 커서를 맨 위로 → 출력 → 남은 아래쪽 지우기)
        print("\033[H\n", end="")
        print(f"enabled            : {action['enabled']!s:<5}   \ngripper_vel: {action['gripper_vel']:+.1f}")
        print(f"phone delta        : {format_pose(phone_delta)}")
        print(f"current robot pose : {format_pose(current_robot_pose)}")
        print(f"new robot pose     : {format_pose(new_robot_pose)}")
        print(f"actual robot pose  : {format_pose(actual_pose)}")
        print("\033[J", end="", flush=True)

def limit_step(last_pos: np.ndarray, new_pos: np.ndarray, max_ee_step: float=MAX_EE_STEP) -> np.ndarray:
    """위치(3개)를 받아서, 직전 위치에서 max_ee_step 보다 멀면 방향은 그대로 두고 길이만 줄인다."""
    dpos = last_pos - new_pos
    n = float(np.linalg.norm(dpos))
    if n > max_ee_step:
        print(f"EE jump {n:.3f}m > {max_ee_step}m; rate-limited")
        dpos = dpos / n * max_ee_step
        return last_pos - dpos
    else:
        return new_pos

def show(viz, robot):
    viz.display(robot.state.q)
    placo_utils.visualization.robot_frame_viz(robot, EE_FRAME)

class IKSolver:
    def __init__(self, robot: placo.RobotWrapper):
        self.robot = robot
        self.solver = placo.KinematicsSolver(robot)
        self.solver.mask_fbase(True)
        self.solver.add_regularization_task(REGULARIZATION_WEIGHT) # task 정규화
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



def main():
    args = parse_args()

    # loading the robot
    robot = placo.RobotWrapper(URDF_PATH, placo.Flags.ignore_collisions)
    iksolver = IKSolver(robot)

    # ── ⑥ 시각화 · 로그 설정 ──────────────────────────────────
    # 시각화는 입력 소스보다 먼저 (핸드폰 connect() 가 캘리브레이션 터치까지 멈추므로 브라우저를 먼저 열어 둔다)
    viz = placo_utils.visualization.robot_viz(robot)
    placo_utils.visualization.frame_viz("world", np.eye(4))

    logger = None
    if args.log == "rerun":
        from test_src.debug_log import DebugLogger
        logger = DebugLogger(web_port=9091)

    # ── ①② 입력 소스 설정 ─────────────────────────────────────
    # 둘 다 같은 모양의 action dict (enabled, target_x..wz, gripper_vel) 를 돌려준다
    if args.source == "phone":
        #phone teleop config
        teleop_config = PhoneConfig(phone_os = PhoneOS.ANDROID)
        teleop_device = Phone(teleop_config)

        # phone -> robot action mapping changer
        phone_to_robot = MapPhoneActionToRobotAction(platform=teleop_config.phone_os)

        # Connecting the phone (캘리브레이션 터치까지 여기서 기다린다)
        teleop_device.connect()

        def read_action():
            phone_obs = teleop_device.get_action()
            return phone_to_robot.action(phone_obs)
    else:
        from test_src.keyboard_ik_viz import KeyboardSource
        keyboard = KeyboardSource()
        read_action = keyboard.get_action

    # ── ④ 클러치 상태 ─────────────────────────────────────────
    phone_to_target = PhoneToTargetPose(robot)
    

    # ── 안전 장치 상태 ─────────────────────────────────────────
    ee_bounds = {"min": [0.0, -0.3, 0.0], "max": [0.3, 0.3, 0.3]}  # end-effector bounds
    last_robot_pose = phone_to_target.current_robot_pose.copy()

    # ── Main loop ────────────────────────────────────────────
    if args.log == "terminal":
        print("\033[2J", end="")  # 화면 전체 지우기 (연결 메시지 정리)
    while True:
        t0 = time.perf_counter()

        # ── ①② 입력 ──
        action = read_action()

        # ── ③ 변화량 ──
        new_robot_pose = phone_to_target.update(robot,action)

        # ── 안전 장치: 공간 제한 → 최대 이동량 ──
        new_robot_pose[:3, 3] = np.clip(new_robot_pose[:3, 3], ee_bounds["min"], ee_bounds["max"])
        new_robot_pose[:3, 3] = limit_step(last_robot_pose[:3, 3], new_robot_pose[:3, 3])
        last_robot_pose = new_robot_pose.copy()  # 다음 프레임의 최대 이동량 비교용

        # ── ⑤ IK ──
        iksolver.solve(new_robot_pose)

        actual_pose = robot.get_T_world_frame(EE_FRAME)

        # ── ⑥ 로그 · 시각화 ──
        print_log(logger, args, action, phone_to_target.phone_delta ,phone_to_target.current_robot_pose, new_robot_pose, actual_pose)
        show(viz, robot)

        precise_sleep(max (1.0 / FPS - (time.perf_counter() - t0), 0.0))

if __name__ == "__main__":
    main()
