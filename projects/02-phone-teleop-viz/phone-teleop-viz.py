
from pprint import pprint
import time

from lerobot.lerobot_types import RobotAction, RobotObservation

# phone library imports
from lerobot.model.kinematics import RobotKinematics
from lerobot.processor.pipeline import RobotProcessorPipeline
from lerobot.robots.so_follower.so_follower import SO100Follower
from lerobot.teleoperators.phone import Phone, PhoneConfig
from lerobot.teleoperators.phone.config_phone import PhoneOS

from typing import TYPE_CHECKING

from lerobot.teleoperators.phone.phone_processor import MapPhoneActionToRobotAction
import pinocchio as pin
import numpy as np

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

def main():
    #phone teleop config
    teleop_config = PhoneConfig(phone_os = PhoneOS.ANDROID)
    teleop_device = Phone(teleop_config)

    # loading the robot
    urdf_path = "projects/02-phone-teleop-viz/so101-description/so101_new_calib.urdf"
    robot = placo.RobotWrapper(urdf_path, placo.Flags.ignore_collisions)

    # Connecting the phone
    teleop_device.connect()

    # phone -> robot action mapping changer
    phone_to_robot = MapPhoneActionToRobotAction(platform=teleop_config.phone_os)

    while True:
        phone_obs = teleop_device.get_action()
        pprint(phone_obs)  

        
        action = phone_to_robot.action(phone_obs)
        t = pin.exp6(np.array([action["target_x"], action["target_y"], action["target_z"], 0.0, 0.0, 0.0])) 
        r = pin.exp6(np.array([0.0, 0.0, 0.0, action["target_wx"], action["target_wy"], action["target_wz"]]))  
        new_pose = np.array(t * r)  # Combine translation and rotation
        pprint(new_pose)

        time.sleep(1)  # Add a small delay to avoid overwhelming the output
    

main()