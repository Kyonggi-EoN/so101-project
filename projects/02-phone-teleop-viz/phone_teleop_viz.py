from pprint import pprint
import time


# phone library imports
from lerobot.robots.so_follower.robot_kinematic_processor import EEReferenceAndDelta
from lerobot.teleoperators.phone import Phone, PhoneConfig
from lerobot.teleoperators.phone.config_phone import PhoneOS

from typing import TYPE_CHECKING

from lerobot.teleoperators.phone.phone_processor import MapPhoneActionToRobotAction
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

def format_pose(T: np.ndarray | None) -> str:
    """4x4 자세를 'pos [x y z]  rot [wx wy wz]' 한 줄로. 위치는 m, 회전은 회전 벡터(rad)."""
    if T is None:
        return "-"
    pos = T[:3, 3]
    rotvec = Rotation.from_matrix(T[:3, :3]).as_rotvec()
    pos_str = " ".join(f"{v:+.3f}" for v in pos)
    rot_str = " ".join(f"{v:+.3f}" for v in rotvec)
    return f"pos [{pos_str}]  rot [{rot_str}]"

def main():
    #phone teleop config
    teleop_config = PhoneConfig(phone_os = PhoneOS.ANDROID)
    teleop_device = Phone(teleop_config)

    # loading the robot
    urdf_path = "projects/02-phone-teleop-viz/so101-description/so101_new_calib.urdf"
    robot = placo.RobotWrapper(urdf_path, placo.Flags.ignore_collisions)

    # phone -> robot action mapping changer
    phone_to_robot = MapPhoneActionToRobotAction(platform=teleop_config.phone_os)

    # Creating the solver
    solver = placo.KinematicsSolver(robot)
    solver.mask_fbase(True)

    ee_task = solver.add_frame_task("gripper_frame_link", np.eye(4))
    ee_task.configure("gripper_frame_link", "soft", 0.5, 0.01)


    # creating the robot viz
    viz = placo_utils.visualization.robot_viz(robot)
        
    # Connecting the phone
    teleop_device.connect()


    # variable to keep track of the enabled state and the current robot pose
    isEnabled = False
    current_robot_pose = None
    new_robot_pose = robot.get_T_world_frame("gripper_frame_link")

    # Main loop
    print("\033[2J", end="")  # 화면 전체 지우기 (연결 메시지 정리)
    while True:
        
        # Get the latest phone action
        phone_obs = teleop_device.get_action()

        # Map the phone action to robot action
        action = phone_to_robot.action(phone_obs)

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

        time.sleep(0.1)  # Add a small delay to avoid overwhelming the output
    

main()