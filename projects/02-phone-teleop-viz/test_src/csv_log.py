"""매 프레임 값을 CSV 로 저장 (조작감 문제 분석용). phone_teleop_viz.py --record 로 켠다.

결과: outputs/teleop_log.csv. Ctrl+C 로 꺼도 그때까지 저장돼 있다 (줄마다 바로 씀)
"""
import csv
import time
from pathlib import Path

import numpy as np

from lerobot.utils.rotation import Rotation

JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
XYZ = ["x", "y", "z"]


def _pos(T):
    return list(np.asarray(T)[:3, 3])


def _rotvec(T):
    return list(Rotation.from_matrix(np.asarray(T)[:3, :3]).as_rotvec())


class CsvRecorder:
    def __init__(self, robot, path: str = "outputs/teleop_log.csv"):
        self.robot = robot
        Path(path).parent.mkdir(exist_ok=True)
        self.f = open(path, "w", newline="", buffering=1)
        self.w = csv.writer(self.f)
        self.w.writerow(["t", "enabled"]
                        + [f"delta_{a}" for a in XYZ] + [f"delta_w{a}" for a in XYZ]
                        + [f"anchor_{a}" for a in XYZ] + [f"target_{a}" for a in XYZ] + [f"actual_{a}" for a in XYZ]
                        + [f"target_w{a}" for a in XYZ] + [f"actual_w{a}" for a in XYZ] + JOINTS)
        self.t0 = time.time()
        print(f"recording: {path}", flush=True)

    def log(self, action, anchor, target, actual):
        self.w.writerow([f"{time.time() - self.t0:.3f}", int(action["enabled"])]
                        + [action[f"target_{a}"] for a in XYZ] + [action[f"target_w{a}"] for a in XYZ]
                        + _pos(anchor) + _pos(target) + _pos(actual) + _rotvec(target) + _rotvec(actual)
                        + [self.robot.get_joint(j) for j in JOINTS])
