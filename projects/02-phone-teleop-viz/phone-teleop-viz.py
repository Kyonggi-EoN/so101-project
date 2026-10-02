
from lerobot.lerobot_types import RobotAction, RobotObservation

# phone library imports
from lerobot.model.kinematics import RobotKinematics
from lerobot.processor.pipeline import RobotProcessorPipeline
from lerobot.robots.so_follower.so_follower import SO100Follower
from lerobot.teleoperators.phone import Phone, PhoneConfig
from lerobot.teleoperators.phone.config_phone import PhoneOS

from typing import TYPE_CHECKING

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
    robot = placo.RobotWrapper("projects/02-phone-teleop-viz/urdf/so101_calib.urdf", placo.Flags.ignore_collision)

    # Creating the solver
    solver = placo.KinematicsSolver(robot)
    solver.mask_fbase(True)  # Fix the base
