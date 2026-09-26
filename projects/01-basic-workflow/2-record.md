# 2. 데이터 녹화
```powershell
uv run lerobot-teleoperate `
    --robot.type=so101_follower --robot.port=COM6 --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --teleop.type=so101_leader --teleop.port=COM5 --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader `
    --robot.cameras="{ top: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30} }" `
    --fps=30 `
    --display_data=true
```
> 위와 같이 display_data=ture를 통해 teleoperate 명령을 하면 rerun이 켜지며 카메라 화면과 모터 움직임 그래프가 나오는 것을 볼 수 있었다.
> 위의 코드는 카메라가 노트북 카메라를 통해 열릴 것이다.
> 이제는 카메라 영상과 실시간으로 기록되는 모터 센서 그래프, 즉 데이터셋을 다루어야한다.
> 아래의 record 명령을 통해 기록이 시작되며 rerun에서 실시간으로 기록 현황을 모니터링 할 수 있다.

```powershell
uv run lerobot-record `
    --robot.type=so101_follower --robot.port=COM6 --robot.id=follower `
    --robot.calibration_dir=calibration/robots/so_follower `
    --teleop.type=so101_leader --teleop.port=COM5 --teleop.id=leader `
    --teleop.calibration_dir=calibration/teleoperators/so_leader `
    --robot.cameras='{ 
        top: {type: opencv, index_or_path: /dev/cam_top, width: 640, height: 480, fps: 25},
        wrist: {type: opencv, index_or_path: /dev/cam_wrist, width: 640, height: 480, fps: 25},
    }' `
    --dataset.single_task=${TASK_NAME} `
    --dataset.repo_id=${HF_USER}/${TASK_NAME} `
    --dataset.num_episodes=10 `
    --dataset.episode_time_s=15 `
    --dataset.reset_time_s=3 `
    --display_data=true `
    --dataset.push_to_hub=false `
    --resume=true

``` > 수정 요망

> 우리가 촬영한 5~15초 짜리 영상 한 개 -> 에피소드
--dataset.episode_time_s=60 : 각 데이터 에피소드 recording 시간 (default: 60초)
--dataset.reset_time_s=60 : 각 에피소드 recording 후, 환경 리셋 시간 (default: 60초).
--dataset.num_episodes=50 : recording할 전체 에피소드 수 (default: 50).
> 각 에피소드를 다음과 같이 내가 설정할 수도 있지만 키보드 조작을 통해 할 수도 있다.

오른쪽 화살표 누르기 (→): 현재 에피소드를 일찍 종료하거나 시간을 재설정하고 다음 에피소드로 넘어갑니다.
왼쪽 화살표 누르기 (←): 현재 에피소드를 취소하고 다시 녹화합니다.
Escape 누르기 (ESC): 세션을 즉시 종료하고, 비디오를 인코딩한 후 데이터셋을 업로드합니다. (tip: Ctrl + c 로 종료하게 되면 망가진 데이터셋이 기록에 남아 학습 오류를 유발합니다.)

> 해당 조작키는 실행되고 있는 터미널에서 입력해야된다. (rerun에서 입력하면 안먹힘)

> 조종하는 모습을 학습용 데이터셋으로 기록하고 Hugging Face 에 올리기.
