"""핸드폰 원본 값 녹화 (방향 클러치·축 매핑 확인용). 로봇·IK 없이 핸드폰만 연결한다.

    GLIBC_TUNABLES=glibc.rtld.execstack=2 uv run python projects/02-phone-teleop-viz/test_src/phone_record.py

결과: outputs/phone_record.csv (한 줄 = 한 프레임, 30Hz)
"""
import csv
import time
from pathlib import Path

from lerobot.teleoperators.phone import Phone, PhoneConfig
from lerobot.teleoperators.phone.config_phone import PhoneOS

SECONDS_PER_STEP = 10
STEPS = [
    "1) 핸드폰을 평평하게(화면 위, 위쪽 끝이 로봇 앞) 들고 → 화면 누른 채 핸드폰 위쪽 끝 방향으로 10cm 밀었다 돌아오기 → 손 떼기",
    "2) 핸드폰을 앞으로 45° 기울여 들고 → 화면 누른 채 '수평으로' 앞으로 10cm 밀었다 돌아오기 → 손 떼기",
    "3) 핸드폰을 평평하게 들고 왼쪽으로 90° 돌린 뒤 → 화면 누른 채 핸드폰 위쪽 끝 방향으로 10cm 밀었다 돌아오기 → 손 떼기",
]

out = Path("outputs/phone_record.csv")
out.parent.mkdir(exist_ok=True)

phone = Phone(PhoneConfig(phone_os=PhoneOS.ANDROID))
phone.connect()  # 캘리브레이션: 평평하게 들고(화면 위, 위쪽 끝이 로봇 앞) 터치한 채 살짝 움직이기
impl = phone._phone_impl

with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t", "step", "enabled", "raw_px", "raw_py", "raw_pz", "raw_qx", "raw_qy", "raw_qz", "raw_qw",
                "cal_px", "cal_py", "cal_pz", "cal_qx", "cal_qy", "cal_qz", "cal_qw",
                "calinv_qx", "calinv_qy", "calinv_qz", "calinv_qw"])
    t0 = time.time()
    for i, text in enumerate(STEPS):
        print(f"\n{text}  ({SECONDS_PER_STEP}초)")
        while time.time() - t0 < (i + 1) * SECONDS_PER_STEP:
            ok, raw_pos, raw_rot, _ = impl._read_current_pose()
            act = phone.get_action()
            if ok and act:
                w.writerow([f"{time.time() - t0:.3f}", i + 1, int(act["phone.enabled"]),
                            *raw_pos, *raw_rot.as_quat(), *act["phone.pos"], *act["phone.rot"].as_quat(),
                            *impl._calib_rot_inv.as_quat()])
            time.sleep(1 / 30)

phone.disconnect()
print(f"\n저장: {out}")
