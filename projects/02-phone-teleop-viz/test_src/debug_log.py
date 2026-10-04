"""
디버깅 로그를 터미널 대신 rerun 뷰어(웹 브라우저)로 보낸다.

rerun 은 lerobot 이 `lerobot-teleoperate --display_data=true` 에서 쓰는 시각화 도구다.
이미 설치돼 있어서 따로 깔 것이 없다.

사용법:
    from debug_log import DebugLogger

    logger = DebugLogger()          # 루프 전에 한 번. 브라우저 주소가 출력된다
    while True:
        ...
        logger.log(action, phone_delta, current_robot_pose, new_robot_pose, actual_pose)
"""

import time

import numpy as np
import rerun as rr

from lerobot.utils.rotation import Rotation

AXES = ["x", "y", "z"]
AXIS_COLORS = [[230, 60, 60], [60, 180, 60], [60, 110, 230]]  # 빨강 x, 초록 y, 파랑 z (meshcat 과 같게)


def _pos(T: np.ndarray | None) -> np.ndarray | None:
    return None if T is None else np.asarray(T)[:3, 3]


def _rotvec(T: np.ndarray | None) -> np.ndarray | None:
    return None if T is None else Rotation.from_matrix(np.asarray(T)[:3, :3]).as_rotvec()


class DebugLogger:
    def __init__(self, app_name: str = "phone_teleop_viz", mode: str = "web", web_port: int = 9090):
        """
        mode="web"   : 브라우저로 보기 (WSL 에서 권장). 출력되는 주소를 Windows 브라우저에서 연다
        mode="spawn" : 별도 창으로 보기 (WSLg 필요)
        """
        rr.init(app_name)

        if mode == "web":
            server_uri = rr.serve_grpc()
            rr.serve_web_viewer(web_port=web_port, open_browser=False, connect_to=server_uri)
            print(f"rerun viewer: http://localhost:{web_port}/?url={server_uri}", flush=True)
        elif mode == "spawn":
            rr.spawn()
        else:
            raise ValueError(f"mode must be 'web' or 'spawn', got {mode!r}")

        # 그래프 선 이름과 색 (한 번만 보내면 된다)
        for entity in ["pos/target", "pos/actual", "pos/anchor", "phone_delta/pos", "rot/target", "rot/actual"]:
            rr.log(entity, rr.SeriesLines(names=AXES, colors=AXIS_COLORS), static=True)

        self._step = 0
        self._start = time.time()
        self._prev_enabled = None

    def log(
        self,
        action: dict,
        phone_delta: np.ndarray | None,
        anchor_pose: np.ndarray | None,
        target_pose: np.ndarray | None,
        actual_pose: np.ndarray | None,
    ) -> None:
        """한 루프의 값들을 기록한다. 자세는 모두 4x4 (없으면 None)."""
        # 시간축: 루프 번호와 경과 시간 둘 다. 뷰어 아래쪽에서 고를 수 있다
        rr.set_time("step", sequence=self._step)
        rr.set_time("time", duration=time.time() - self._start)
        self._step += 1

        enabled = bool(action.get("enabled", False))

        # 버튼 상태 (0 / 1) 와 그리퍼 명령
        rr.log("input/enabled", rr.Scalars(float(enabled)))
        rr.log("input/gripper_vel", rr.Scalars(float(action.get("gripper_vel", 0.0))))

        # 누르는 순간 / 손 뗀 순간을 텍스트 로그로
        if self._prev_enabled is not None and enabled != self._prev_enabled:
            rr.log("events", rr.TextLog("pressed (anchor 저장)" if enabled else "released (목표 유지)"))
        self._prev_enabled = enabled

        # 위치 (m): 목표 vs 실제가 핵심. 둘이 벌어지면 IK 가 못 따라가는 것
        for name, T in [("target", target_pose), ("actual", actual_pose), ("anchor", anchor_pose)]:
            p = _pos(T)
            if p is not None:
                rr.log(f"pos/{name}", rr.Scalars(p))

        # 회전 (회전 벡터, rad)
        for name, T in [("target", target_pose), ("actual", actual_pose)]:
            w = _rotvec(T)
            if w is not None:
                rr.log(f"rot/{name}", rr.Scalars(w))

        # 핸드폰 변화량 위치 (m)
        p = _pos(phone_delta)
        if p is not None:
            rr.log("phone_delta/pos", rr.Scalars(p))

        # IK 오차 (cm): 목표와 실제 위치의 거리
        if target_pose is not None and actual_pose is not None:
            err_cm = float(np.linalg.norm(_pos(target_pose) - _pos(actual_pose)) * 100)
            rr.log("ik/pos_error_cm", rr.Scalars(err_cm))
