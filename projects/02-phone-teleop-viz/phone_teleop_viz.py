"""
실행 (리포 루트에서):
    # 핸드폰으로 조종, 로그는 터미널
    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone_teleop_viz.py

    # 키보드로 테스트 (핸드폰 불필요), 로그는 rerun 웹 뷰어
    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/phone_teleop_viz.py --source keyboard

    # 키보드 명령: on / off / x0.1 / y0.1 / z0.05
"""
import argparse
from pprint import pprint
import time


# phone library imports
from lerobot.robots.so_follower.robot_kinematic_processor import EEBoundsAndSafety, EEReferenceAndDelta
from lerobot.teleoperators.phone import Phone, PhoneConfig
from lerobot.teleoperators.phone.config_phone import PhoneOS

from typing import TYPE_CHECKING

from lerobot.teleoperators.phone.phone_processor import MapPhoneActionToRobotAction
from lerobot.utils.robot_utils import precise_sleep
from lerobot.utils.rotation import Rotation
import pinocchio as pin
import numpy as np
import placo_utils.visualization

_placo_runtime_error: ImportError | None = None

if TYPE_CHECKING:
    import placo  # type: ignore[import-not-found]
else:
    try:
        import placo  # type: ignore[import-not-found]
    except ImportError as _placo_import_err:
        _placo_runtime_error = _placo_import_err
        raise ImportError(
                    f"uv sync --extra placo-dep --extra phone"
                    # f"placo is installed but failed to import: {_placo_runtime_error!s}"
                ) from _placo_runtime_error

FPS = 30.0

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
                        help="로그 출력 위치. 기본값: phone → terminal, keyboard → rerun (터미널은 키보드 입력과 충돌)")
    args = parser.parse_args()
    if args.log is None:
        args.log = "rerun" if args.source == "keyboard" else "terminal"
    return args

def main():
    args = parse_args()

    # loading the robot
    urdf_path = "projects/02-phone-teleop-viz/so101-description/so101_new_calib.urdf"
    robot = placo.RobotWrapper(urdf_path, placo.Flags.ignore_collisions)

    # Creating the solver
    solver = placo.KinematicsSolver(robot)
    solver.mask_fbase(True)
    solver.add_regularization_task(0.000001) # task 정규화
    solver.enable_velocity_limits(True)
    solver.dt = 1 / FPS

    ee_task = solver.add_frame_task("gripper_frame_link", np.eye(4))
    ee_task.configure("gripper_frame_link", "soft", 0.5, 0.01)

    # robot bounds and safety
    ee_bounds = {"min": [-1.0, -1.0, -1.0], "max": [1.0, 1.0, 1.0]}  # end-effector bounds
    max_ee_step = 0.05

    # creating the robot viz
    viz = placo_utils.visualization.robot_viz(robot)

    # log output
    if args.log == "rerun":
        from test_src.debug_log import DebugLogger
        logger = DebugLogger()

    # input source: 둘 다 같은 모양의 action dict (enabled, target_x..wz, gripper_vel) 를 돌려준다
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

    # variable to keep track of the enabled state and the current robot pose
    isEnabled = False
    current_robot_pose = None
    new_robot_pose = robot.get_T_world_frame("gripper_frame_link")

    placo_utils.visualization.frame_viz("world", np.eye(4))

    # Main loop
    if args.log == "terminal":
        print("\033[2J", end="")  # 화면 전체 지우기 (연결 메시지 정리)
    while True:
        t0 = time.perf_counter()

        # Get the latest action (phone or keyboard)
        action = read_action()

        # Comput phone delta
        t = pin.exp6(np.array([action["target_x"], action["target_y"], action["target_z"], 0.0, 0.0, 0.0])) 
        r = pin.exp6(np.array([0.0, 0.0, 0.0, action["target_wx"], action["target_wy"], action["target_wz"]]))  
        phone_delta = np.array(t * r)  # Combine translation and rotation

        # Get the current pose of the robot's end-effector
        # p + Δp 방법 사용, p + R·Δp는 테스트 예정
        if action["enabled"]:
            if not isEnabled:
                # Store the current pose when enabled is first pressed
                current_robot_pose = robot.get_T_world_frame("gripper_frame_link")  # Get the current pose of the robot's end-effector
                new_robot_pose = current_robot_pose @ np.array(r)   # 회전 행렬곱
                new_robot_pose[:3, 3] = new_robot_pose[:3, 3] + np.array(t)[:3, 3] # 위치 이동
                isEnabled = True
            else:
                # Update the new pose based on the stored current pose and the phone delta
                new_robot_pose = current_robot_pose @ np.array(r)   # 회전 행렬곱
                new_robot_pose[:3, 3] = new_robot_pose[:3, 3] + np.array(t)[:3, 3]    # 위치 이동
        else:
            if isEnabled:
                # When the button is released, maintain the last pose
                current_robot_pose = robot.get_T_world_frame("gripper_frame_link")
                isEnabled = False

        isEnabled = action["enabled"]

        ee_task.T_world_frame = new_robot_pose  # Update the task with the new pose
        
        #  solving the IK
        solver.solve(True)

        # update pose of the robot's end-effector
        robot.update_kinematics()

        # Get the actual pose for log
        actual_pose = robot.get_T_world_frame("gripper_frame_link")

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

        viz.display(robot.state.q)
        placo_utils.visualization.robot_frame_viz(robot, "gripper_frame_link")

        precise_sleep(max (1.0 / FPS - (time.perf_counter() - t0), 0.0))

main()