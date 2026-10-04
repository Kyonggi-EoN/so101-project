import threading

class KeyboardSource:
    def __init__(self):
        self._lock = threading.Lock()
        self._latest = {
            "enabled": False,
            "target_x": 0.0,
            "target_y": 0.0,
            "target_z": 0.0,
            "target_wx": 0.0,
            "target_wy": 0.0,
            "target_wz": 0.0,
            "gripper_vel": 0.0,
        }
        threading.Thread(target=self._input_loop, daemon=True).start()

    def _input_loop(self):                 # 입력 스레드가 실행
        while True:
            line = input("> ")

            if line.startswith("x"):
                try:
                    value = float(line[1:])
                    new = dict(self._latest)
                    new["target_x"] = value
                except ValueError:
                    print("Invalid x value")
            elif line.startswith("y"):  
                try:
                    value = float(line[1:])
                    new = dict(self._latest)
                    new["target_y"] = value
                except ValueError:
                    print("Invalid y value")
            elif line.startswith("z"):
                try:
                    value = float(line[1:])
                    new = dict(self._latest)
                    new["target_z"] = value
                except ValueError:
                    print("Invalid z value")        
            elif line == "on" :
                new = {
                    "target_x": 0.0,
                    "target_y": 0.0,
                    "target_z": 0.0,
                    "target_wx": 0.0,
                    "target_wy": 0.0,
                    "target_wz": 0.0,
                    "gripper_vel": 0.0,
                    "enabled": True,
                }
            elif line == "off":
                new = {
                    "target_x": 0.0,
                    "target_y": 0.0,
                    "target_z": 0.0,
                    "target_wx": 0.0,
                    "target_wy": 0.0,
                    "target_wz": 0.0,
                    "gripper_vel": 0.0,
                    "enabled": False,
                }
            else:
                print("Invalid command. Use 'x<value>', 'y<value>', 'z<value>', 'on', or 'off'.")
                continue


            with self._lock:
                self._latest = new          # 통째로 교체

    def get_action(self):                  # 메인 루프가 호출
        with self._lock:
            return dict(self._latest)       # 복사해서 돌려줌
